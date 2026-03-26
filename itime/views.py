from django.contrib.auth.decorators import login_required
from accounts.decorators import tool_access_required

from django.shortcuts import render, redirect
from django.contrib import messages
from staff.models import ValidationTeamMember
from projects.models import Project
from .models import itime
import datetime
from .utils import generate_attendance_excel

# Create your views here.

# I-TIME main page
@login_required
@tool_access_required('can_access_iTime_tool','dashboard')
def itime_page(request):

    # 1. Get employee ID
    try:
        current_employee = ValidationTeamMember.objects.get(profile=request.user.profile)
        is_validation = True
    except (ValidationTeamMember.DoesNotExist, AttributeError):
        current_employee = None
        is_validation = False

    # project list for Form
    projects = Project.objects.filter(is_completed="ongoing")

    # 3. If form was submitted
    if request.method == 'POST':
        if is_validation:
            record, created = itime.objects.get_or_create(
                employee=current_employee,
                date=datetime.date.today()
            )     

            selected_projects = request.POST.getlist('projects')  

            if selected_projects:
                for project_id in selected_projects:
                    if project_id.isdigit():
                        record.projects.add(project_id)
                
                record.save()
                messages.success(request,"Checked-in sucessfully")

            else:
                messages.success(request, "Checked-in successfully with no projects")
            return redirect('itime')

    context = {
        'is_validation' : is_validation,
        'current_employee' : current_employee,
        'all_projects' : projects,

    }

    # ITime records for this user
    if is_validation:
        context['records'] = itime.objects.filter(employee=current_employee).order_by('-date')
    else:
        context['all_records'] = itime.objects.order_by('-date', 'employee__name')

   
    return render(request, 'itime.html', context)


# Mark all as exported
@login_required
@tool_access_required('can_mark_iTime_as_exported', 'itime')
def itime_mark_all_as_exported(request):

    records = itime.objects.filter(is_exported=False).select_related('employee').prefetch_related('projects__field_manager')
    if not records.exists():
        messages.warning(request, "No pending records.")
        return redirect('itime')
    
    excel_file_response = generate_attendance_excel(records) 

    updated_count = records.update(is_exported=True)
    return excel_file_response


# Export Attendance sheet
@login_required
@tool_access_required('can_export_iTime_sheet', 'itime')
def itime_export_excel(request):
    records = itime.objects.filter(is_exported=False).select_related('employee').prefetch_related('projects__field_manager')

    if not records.exists():
        from django.contrib import messages
        messages.warning(request, "No pending records to export.")
        return redirect('itime')
    
    excel_file_response = generate_attendance_excel(records)

    return excel_file_response