from django.contrib.auth.decorators import login_required
from accounts.decorators import tool_access_required
import os
import zipfile
from io import BytesIO
from django.http import FileResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import ProjectForm
from .models import Project, ProjectFiles


# Create your views here.
# The main Page 
@login_required
@tool_access_required('can_access_Projects_tool', 'dashboard')
def projects_list(request):
    project_name = request.GET.get('project')
    manager_id = request.GET.get('field_manager')
    p_type = request.GET.get('project_type')
    status = request.GET.get('status')
    date_query = request.GET.get('date')

    projects = Project.objects.select_related('field_manager').all()

    if project_name:
        projects = projects.filter(name__icontains=project_name)
    if manager_id:
        projects = projects.filter(field_manager_id=manager_id)
    if p_type:
        projects = projects.filter(project_type=p_type)
    if status:
        projects = projects.filter(is_completed=status)
    if date_query:
        projects = projects.filter(created_at__date=date_query)

 
    managers_list = Project.objects.values(
    'field_manager__id', 
    'field_manager__name'
    ).distinct().order_by('field_manager__name')

    context = {
        'projects': projects,
        'managers_list': managers_list, 
        'project_types': Project.PROJECT_TYPE_CHOICES,
        'status_choices': Project.STATUS_CHOICES,
        'is_searching': any([project_name, manager_id, p_type, status, date_query])
    }

    return render(request, 'projects_list.html', context)

# Add Project Page
@login_required
@tool_access_required('can_access_Projects_tool', 'dashboard')
def projects_add(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES) 

        if form.is_valid():
            project = form.save()
            files = request.FILES.getlist('project_files')
            for f in files:
                ProjectFiles.objects.create(project=project, file=f)
            messages.success(request, "Project added successfully!")
            return redirect('projects_list')
    else:
        form = ProjectForm()

    context = {
        'form': form,
        'title': 'Add New Project'
    }
    return render(request, 'projects_add.html', context)

# Edit Project app
@login_required
@tool_access_required('can_access_Projects_tool', 'dashboard')
def projects_edit(request, pk):

    project = get_object_or_404(Project, pk=pk)

    if request.method == 'POST':
            form = ProjectForm(request.POST, request.FILES, instance=project)

            if form.is_valid():
                updated_project = form.save()

                files = request.FILES.getlist('project_files')
                for f in files:
                    ProjectFiles.objects.create(project=updated_project, file=f)

                messages.success(request, f"Project '{project.name}' updated successfully!")
                return redirect('projects_list')
            else:
                print("Form Errors:", form.errors.as_data()) 
                print("Files received:", request.FILES)
    else:
        form = ProjectForm(instance=project)
    
    context = {
        'form': form,
        'project': project,
        'title': 'Edit Project'
    }
    return render(request, 'projects_edit.html', context)

# Downaload project files likes .mtt...
@login_required
@tool_access_required('can_access_Projects_tool', 'dashboard')
def projects_download_files(request, pk):
    project = get_object_or_404(Project, pk=pk)
    project_files = project.files.all() 

    if not project_files.exists():
        messages.error(request, 'No files attached to this project.')
        return redirect(request.META.get('HTTP_REFERER', 'projects_list'))

    if project_files.count() == 1:
        file_obj = project_files.first().file
        if os.path.exists(file_obj.path):
            return FileResponse(open(file_obj.path, 'rb'), as_attachment=True)

    byte_data = BytesIO()
    with zipfile.ZipFile(byte_data, 'w') as zip_file:
        for obj in project_files:
            if os.path.exists(obj.file.path):
                zip_file.write(obj.file.path, arcname=os.path.basename(obj.file.name))
    
    byte_data.seek(0)
    response = HttpResponse(byte_data, content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{project.name}_files.zip"'
    
    return response