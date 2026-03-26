from django.urls import path
from . import views

urlpatterns = [
    path('itime/', views.itime_page, name='itime'),
    path('itime/mark_as_exported', views.itime_mark_all_as_exported, name='itime_mark_as_exported'),
    path('itime/exporte_excel', views.itime_export_excel, name='itime_export_excel'),
    

]