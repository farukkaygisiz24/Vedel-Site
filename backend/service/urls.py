from django.urls import path, register_converter

from . import views


class JobNumberConverter:
    regex = r'(?:[sS][rR][vV]|[sS][aA][lL])[0-9]{8,}'

    def to_python(self, value):
        return str(value).upper()

    def to_url(self, value):
        return ''.join(ch for ch in str(value).lower() if ch.isalnum())


register_converter(JobNumberConverter, 'job_no')

urlpatterns = [
    path('', views.schedule, name='portal-service'),
    path('clients/', views.client_list, name='portal-service-clients'),
    path('jobs/', views.job_list, name='portal-service-jobs'),
    path('jobs/new/', views.job_new, name='portal-service-job-new'),
    path('jobs/<job_no:number>/', views.job_detail, name='portal-service-job-detail'),
    path('reminders/', views.reminders, name='portal-service-reminders'),
    path('reminders/summary/', views.reminders_summary, name='portal-service-reminders-summary'),
    path('devices/', views.device_list_json, name='portal-service-devices'),
]
