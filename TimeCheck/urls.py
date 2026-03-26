from django.urls import path
from . import views

urlpatterns = [
    path('time-check/', views.timecheck, name='timecheck'),
    path('timecheck-process/', views.timecheck_process, name='process-timecheck'),
    path('time-check/results', views.timecheck_view_results_list, name='timecheckResultsList'),
    path('time-check/results/<int:pk>/', views.timecheck_view_results_detail, name='timecheckResultsDetail'),
    path('time-check/results/export-excel/<int:pk>/', views.timecheck_export_validation_excel, name='timecheckexport_excel'),
]


