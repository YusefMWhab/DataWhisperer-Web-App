import pandas as pd
from django.http import HttpResponse


def generate_attendance_excel(records):
    data_attendance = []
    all_projects_data = [] 
    seen_projects = set()

    for record in records:
        project_details = []
        for p in record.projects.all():
            manager_name = p.field_manager.name if p.field_manager else "N/A"
            detail_str = f"{p.name} ({p.get_project_type_display()}) - Mgr: {manager_name}"
            project_details.append(detail_str)
            
            if p.id not in seen_projects:
                all_projects_data.append({
                    'Project Name': p.name,
                    'Project Type': p.get_project_type_display(),
                    'Field Manager': manager_name
                })
                seen_projects.add(p.id)

        data_attendance.append({
            'Employee Name': record.employee.name,
            'Date': record.date,
            'Projects Details': "\n".join(project_details) or "No Projects",
        })

    df_attendance = pd.DataFrame(data_attendance)
    
    df_attendance['Date'] = pd.to_datetime(df_attendance['Date'])

    df_summary = df_attendance.groupby('Employee Name')['Date'].nunique().reset_index()
    df_summary.columns = ['Employee Name', 'Total Working Days']

    df_attendance['Date'] = df_attendance['Date'].dt.strftime('%Y-%m-%d')

    df_projects = pd.DataFrame(all_projects_data)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="Attendance_Full_Report.xlsx"'

    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df_attendance.to_excel(writer, sheet_name='Daily_Attendance', index=False)
        df_summary.to_excel(writer, sheet_name='Employee_Work_Summary', index=False)
        df_projects.to_excel(writer, sheet_name='Projects_List', index=False)
        
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            for col in worksheet.columns:
                max_length = 0
                column = col[0].column_letter
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except: pass
                worksheet.column_dimensions[column].width = max_length + 5

    return response
    