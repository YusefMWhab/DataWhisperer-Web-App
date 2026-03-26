import pandas as pd
import datetime
import json
from django.contrib.auth import get_user_model
from celery import shared_task
from .models import TimeCheckValidationResult
from staff.models import FieldManager
from io import BytesIO


# The main function to handle all time check processes
#@shared_task(name='TimeCheck.utils.TimeCheckProcess')
@shared_task
def TimeCheckProcess (Data_Block, user_id):
    try:
        # 1. Get user name
        User = get_user_model()
        current_user = User.objects.get(id=user_id)

        # 2. Extract Data from Data Block
        field_manager_id = Data_Block.get('field_manager_id')
        user_mapping = Data_Block.get('user_mapping') # Key:Value
        raw_data = Data_Block.get('data') # Array of Objects
        

        # 3. Get Field manager name
        field_manager_obj = FieldManager.objects.get(id=field_manager_id)

        # 4. Convert to DF and sort it
        df = pd.DataFrame(raw_data)

        # 5. Convert Date, time and Length columns to right format
        df[user_mapping["date"]] = pd.to_datetime(df[user_mapping["date"]]).dt.date
        df[user_mapping["start_time"]] = pd.to_datetime(df[user_mapping["start_time"]])
        df[user_mapping["end_time"]] = pd.to_datetime(df[user_mapping["end_time"]])
        df[user_mapping["interview_length"]] = pd.to_numeric(df[user_mapping["interview_length"]], errors='coerce').fillna(0)
        df[user_mapping["interview_active_length"]] = pd.to_numeric(df[user_mapping["interview_active_length"]], errors='coerce').fillna(0)

        columns_to_sort = [
            user_mapping["interviewer_id"],
            user_mapping["date"],
            user_mapping["start_time"]
        ]
        
        df.sort_values(by=columns_to_sort, ascending=True, inplace=True)
        df.reset_index(drop=True, inplace=True)

        

    except Exception as e:
        pass
    
    # 6. CheckConflictInterviews
    statues, msg, conflictResults = CheckConflictInterviews(df, user_mapping)

    if statues == False:
        conflictResults = [{"Error": msg}]
    
    # 7. Daily count report
    statues, msg, DailyCountReportResults = DailyCountReport(df, user_mapping)

    if statues == False:
        DailyCountReportResults = [{"Error": msg}]

    # 8. Out-Working-Hours report
    statues, msg, out_working_hoursResults = out_of_working_hours_check(df, user_mapping)

    if statues == False:
        out_working_hoursResults = [{"Error": msg}]

    # 8. LOI report
    statues, msg, loiResults = active_time_check(df, user_mapping)

    if statues == False:
        loiResults = [{"Error": msg}]


    # Prepare and Save results to Data Base


    validation_record = TimeCheckValidationResult.objects.create(
        
        user = current_user,
        
        field_manager = field_manager_obj,
        
        field_manager_name_snapshot = field_manager_obj.name,
        
        overlap_report = json.dumps(conflictResults, ensure_ascii=False),
        
        daily_count_report = json.dumps(DailyCountReportResults, ensure_ascii=False),
        
        out_working_hours_report = json.dumps(out_working_hoursResults, ensure_ascii=False),
        
        loi_report = json.dumps(loiResults, ensure_ascii=False),

        project_names = list(df[user_mapping["script_name"]].unique()),
        
        raw_data = json.dumps(raw_data, ensure_ascii=False) 
    )


# This method is for CheckConflictInterviews
def CheckConflictInterviews (df, user_mapping):

    try:

        # Get Variables from user_mapping 
        method = user_mapping["technique"]
        threshold = int(user_mapping["sensitivity"])

        # Clear the previous Results
        conflicts_list = []


        for index in range(len(df) - 4):
            # the First Data:
            Serial1 = df.loc[index, user_mapping["instance_id"]]
            Interviewer1 = df.loc[index, user_mapping["interviewer_id"]]
            Script1 = df.loc[index, user_mapping["script_name"]]
            Date1 = df.loc[index, user_mapping["date"]]
            StartTime1 = df.loc[index, user_mapping["start_time"]]
            
            # Get End time based on Start End time technique
            if method == "start-end-time":
                EndTime1 = df.loc[index, user_mapping["end_time"]]
            # Get End time based on interview length technique
            elif method == "interview-length":
                EndTime1 = df.loc[index, user_mapping["start_time"]] + pd.to_timedelta(df.loc[index, user_mapping["interview_length"]], unit="m")

            for idx in range(index + 1, min(index + 5, len(df))):
                Interviewer2 = df.loc[idx, user_mapping["interviewer_id"]]
                # Check only for the same interviewer ID
                if Interviewer1.lower() != Interviewer2.lower():
                    break
                else:
                    # the Second Data:
                    Serial2 = df.loc[idx, user_mapping["instance_id"]]
                    Script2 = df.loc[idx, user_mapping["script_name"]]
                    Date2 = df.loc[idx, user_mapping["date"]]
                    StartTime2 = df.loc[idx, user_mapping["start_time"]]

                    # Get End time based on Start End time technique
                    if method == "start-end-time":
                        EndTime2 = df.loc[idx, user_mapping["end_time"]]
                    # Get End time based on interview length technique
                    elif method == "interview-length":
                        EndTime2 = df.loc[idx, user_mapping["start_time"]] + pd.to_timedelta(df.loc[idx, user_mapping["interview_length"]], unit="m")

                    if EndTime1 > StartTime2 and Date1 == Date2:

                        ConflictTime = EndTime1 - StartTime2
                        # Check The limit based on Time Variable Slider
                        if ConflictTime <= datetime.timedelta(minutes=threshold):
                            continue
                        else:
                            # Store the conflicts
                            # New Row to be added to results Data Frame
                            new_row = {
                                "Interviewer ID" : str(Interviewer1),
                                "Inistance ID 1" : int(Serial1),
                                "Script Name 1" : str(Script1),
                                "Date 1" : str(Date1),
                                "Start Time 1" : str(StartTime1),
                                "End Time 1" : str(EndTime1),
                                "Inistance ID 2" : int(Serial2),
                                "Script Name 2" : str(Script2),
                                "Date 2" : str(Date2),
                                "Start Time 2" : str(StartTime2),
                                "End Time 2" : str(EndTime2),
                                "Conflict Time in min" : float(ConflictTime.total_seconds() / 60)
                            }

                            conflicts_list.append(new_row)
        
        if conflicts_list:
            msg = "Success"
            return True, msg, conflicts_list
        else:
            msg = "Success"
            return True, msg, []
    
    except Exception as e:
        msg = str(e)
        return False, msg, []


# This method is for DailyCountReport
def DailyCountReport(df, user_mapping):

    try:
        # 1. Get headers
        interviewer_col = user_mapping["interviewer_id"]
        date_col = user_mapping["date"]
        instance_col = user_mapping["instance_id"]
        start_time_col = user_mapping["start_time"]

        df[date_col] = pd.to_datetime(df[date_col])
        df[start_time_col] = pd.to_datetime(df[start_time_col])

        # 2. Group by and count
        df_results = df.groupby([interviewer_col, date_col]).agg(
            Number_of_Interviews=(instance_col, 'count'),
            From_Time=(start_time_col, 'min'),
            To_Time=(start_time_col, 'max')
        ).reset_index()
        
        # 3. Convert time to HH:MM Format
        df_results['From_Time'] = df_results['From_Time'].dt.strftime("%H:%M")
        df_results['To_Time'] = df_results['To_Time'].dt.strftime("%H:%M")

        # 4. Time to string
        df_results[date_col] = df_results[date_col].dt.strftime("%Y-%m-%d")

        # 5. Sorting
        df_results = df_results.sort_values(
            by=['Number_of_Interviews'],
            ascending=False,
            ignore_index=True
        )

        # 6. Final result list
        final_list = df_results.rename(columns={
            interviewer_col: 'Interviewer ID',
            date_col: 'Date',
            'Number_of_Interviews': 'Number of Interivews',
            'From_Time': 'First Start Time',
            'To_Time': 'Last Start Time'
        }).to_dict(orient='records')

        msg = "Success"
        return True, msg, final_list
    
    except Exception as e:
        msg = str(e)
        return False, msg, [] 

# This method is for Out-working hours report
def out_of_working_hours_check(df, user_mapping):

    results_list = []
    
    try:
        # 1. Get headers
        interviewer_col = user_mapping["interviewer_id"]
        instance_col = user_mapping["instance_id"]
        start_time_col = user_mapping["start_time"]

        if not start_time_col:
            msg = "Empty Time column"
            return True, msg, []

        # 3. Filter time between 12AM to 6 AM
        off_hours_mask = df[start_time_col].dt.hour.between(0, 5)
        df_off_hours = df[off_hours_mask]

        if df_off_hours.empty:
            msg = "Success with no issues"
            return True, msg, []

        # 4. Convert to python Data Types
        for _, row in df_off_hours.iterrows():
                
            results_list.append({
                "Inistance ID": str(row.get(instance_col, "N/A")),
                "Interviewer ID": str(row.get(interviewer_col, "N/A")),
                "Date": row[start_time_col].strftime('%Y-%m-%d'),
                "Start Time": row[start_time_col].strftime('%H:%M:%S'),
                "Issue Type": "Out of Working Hours",
                "Details": f"Interview started at {row[start_time_col].strftime('%I:%M %p')}"
            })

        msg = "Success"
        return True, msg, results_list
    
    except Exception as e:
        msg = str(e)
        return False, msg, [] 
    
# This method is for LOI report
def active_time_check(df, user_mapping):

    try:
        # 1. Get headers
        interviewer_col = user_mapping["interviewer_id"]
        project_col = user_mapping["script_name"]
        active_time_col = user_mapping["interview_active_length"]
        
        # 2. (Project Average) 
        project_means = df.groupby(project_col)[active_time_col].mean().round(2).to_dict()
        
        # 3. (Interviewer Average)
        grouped = df.groupby([project_col, interviewer_col]).agg(
            Interviewer_Avg=(active_time_col, 'mean'),
            Total_Interviews=(active_time_col, 'count')
        ).reset_index()

        active_time_results = []

        # 4. Save results
        for _, row in grouped.iterrows():
            p_avg = project_means.get(row[project_col], 0)
            i_avg = row['Interviewer_Avg']
            
            deviation_pct = 0
            if p_avg > 0:
                deviation_pct = ((i_avg - p_avg) / p_avg) * 100

            if deviation_pct > 0:
                status = "Above"
            elif deviation_pct < 0:
                status = "Below"
            else:
                status = "Equal"

            new_row = {
                "Script Name": str(row[project_col]),
                "Interviewer ID": str(row[interviewer_col]),
                "Avg Interview Length": float(round(row['Interviewer_Avg'], 2)),
                "Total Interviews": int(row['Total_Interviews']),
                "Project Global Avg": float(project_means.get(row[project_col], 0)),
                "Deviation Pct": float(round(deviation_pct, 2)),
                "Status": f"{abs(round(deviation_pct, 1))}% {status} Avg"
            }
            active_time_results.append(new_row)
        msg = "Success"
        return True, msg, active_time_results
    
    except Exception as e:
        msg = str(e)
        return False, msg, [] 
    
# This method is to build excel report
def SaveExcelReport(record):
    # 2. Extract Data from DB
    data_sheet = {
    '1. Raw Data': json.loads(record.raw_data) if record.raw_data else [],
    '2. Conflicts Report': json.loads(record.overlap_report) if record.overlap_report else [],
    '3. Daily Report': json.loads(record.daily_count_report) if record.daily_count_report else [],
    '4. Working Hours Report': json.loads(record.out_working_hours_report) if record.out_working_hours_report else [],
    '5. LOI Analysis': json.loads(record.loi_report) if record.loi_report else []
}

    output = BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for sheet_name, data in data_sheet.items():
                df = pd.DataFrame(data)

                if not df.empty:
                    
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    
                    worksheet = writer.sheets[sheet_name]
                    for col in worksheet.columns:
                        max_len = 0
                        column = col[0].column_letter 
                        for cell in col:
                            try:
                                if cell.value and len(str(cell.value)) > max_len:
                                    max_len = len(str(cell.value))
                            except: pass
                        worksheet.column_dimensions[column].width = max_len + 2
                else:
                    # لو الشيت فاضي
                    pd.DataFrame(['No data found for this report']).to_excel(writer, sheet_name=sheet_name, index=False, header=False)

    output.seek(0)
    # بنرجع الـ output وتاريخ الإنشاء لاسم الملف
    return output, record.created_at.strftime('%Y%m%d')