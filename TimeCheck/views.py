from django.contrib.auth.decorators import login_required
from accounts.decorators import tool_access_required

import json
from django.template import loader
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, JsonResponse
from staff.models import FieldManager
from .models import TimeCheckValidationResult

from .utils import TimeCheckProcess, SaveExcelReport


# Create your views here.

# Return the main template of Time Check
@login_required
@tool_access_required('can_access_time_check_tool', 'dashboard')
def timecheck(request):
    
    template = loader.get_template('timecheck.html')

    context = {
        'fieldManagers' : FieldManager.objects.all()
        
    }
    return HttpResponse(template.render(context, request))

# Recieve the data and start time check validation
@login_required
@tool_access_required('can_access_time_check_tool', 'dashboard')
def timecheck_process(request):
    if request.method == 'POST':
            
            try:
                
                # 1. Get Data
                data = json.loads(request.body)

                # 2. Call the Validation Task
                TimeCheckProcess.apply_async(args=[data, request.user.id])


                return JsonResponse({
                    'status': 'success',
                    'message': 'Everything is working! Data received and parsed.',
                })
            
            except Exception as e:
                  print(f"ERROR IN TIMECHECK: {str(e)}")
                  return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Only POST allowed'}, status=405)

# Return the Results list template of Time Check
@login_required
@tool_access_required('can_access_time_check_tool', 'dashboard')
def timecheck_view_results_list(request):

    # 1. Get the template
    template = loader.get_template('timecheckResultsList.html')

    # 2. Get all records from DB
    query = TimeCheckValidationResult.objects.all().order_by('-created_at')
    
    # 3. Prepare View data
    managers_list = TimeCheckValidationResult.objects.values_list('field_manager_name_snapshot', flat=True).order_by().distinct()
    users_list = TimeCheckValidationResult.objects.values_list('user__profile__full_name', flat=True).order_by().distinct()

    # 4. Recieve filter form values (Get Request)
    p_name = request.GET.get('project')
    fm_name = request.GET.get('field_manager')
    u_name = request.GET.get('username')
    v_date = request.GET.get('date')

    # 5. Filtered Query
    filtered_query = query
    if p_name:
        filtered_query = filtered_query.filter(project_names__icontains = p_name)
    if fm_name:
        filtered_query = filtered_query.filter(field_manager_name_snapshot = fm_name)
    if u_name:
        filtered_query = filtered_query.filter(user__profile__full_name = u_name)
    if v_date:
        filtered_query = filtered_query.filter(created_at__date = v_date)

    # 6. Check if any search is required or display the last 5 records
    is_searching = any([p_name, fm_name, u_name, v_date])
    
    if is_searching:
        records = filtered_query
    else:
        records = query[:10]

    context = {
        'records': records,
        'managers_list': sorted(filter(None, managers_list)),
        'users_list': sorted(filter(None, users_list)),
        'is_searching': is_searching,    
    }
    
    for rec in records:
        print(f"ID: {rec.id} | Time: {rec.created_at}")

    return HttpResponse(template.render(context, request))

# Return the Results template of Time Check Result Details 
@login_required
@tool_access_required('can_access_time_check_tool', 'dashboard')
def timecheck_view_results_detail(request, pk):

    # 1. Get the template
    template = loader.get_template('timecheckResultsDetail.html')

    # 2. Get query
    query = get_object_or_404(TimeCheckValidationResult, pk=pk)

    # 3. Row Data only 10 rows are fine 
    try:
        full_data = json.loads(query.raw_data) if query.raw_data else []
    except:
        full_data = []

    preview_row_data = full_data[:20]

    # 3. Conflict report review
    try:
        preview_conflict_report = json.loads(query.overlap_report) if query.overlap_report else []

    except:
        preview_conflict_report = []

    # 4. Daily count report review
    try:
        preview_daily_count_report = json.loads(query.daily_count_report) if query.daily_count_report else []

    except:
        preview_daily_count_report = []

    # 5. Out-Hours report review
    try:
        preview_out_hours_report = json.loads(query.out_working_hours_report) if query.out_working_hours_report else []

    except:
        preview_out_hours_report = []

    # 5. Out-Hours report review
    try:
        preview_loi_report = json.loads(query.loi_report) if query.loi_report else []

    except:
        preview_loi_report = []

    context = {
        'preview_row_data' : preview_row_data,
        'preview_conflict_report' : preview_conflict_report,
        'preview_daily_count_report' : preview_daily_count_report,
        'preview_out_hours_report' : preview_out_hours_report,
        'preview_loi_report' : preview_loi_report,  
        'record_pk' : query.pk,
    }

    return HttpResponse(template.render(context, request))

# # Return the Excel file
@login_required
@tool_access_required('can_access_time_check_tool', 'dashboard')
def timecheck_export_validation_excel(request, pk):
    
    # 1. Get query
    query = get_object_or_404(TimeCheckValidationResult, pk=pk)

    # 2. Call the function to build excel file
    output, filename_date = SaveExcelReport(query)

    # 3. Finalizing Response
    filename = f"TimeCheck_Report_{pk}_{filename_date}.xlsx"
    
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response

