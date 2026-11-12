from django.urls import path

from . import field_views

urlpatterns = [
    path('', field_views.field_home, name='portal-field'),
    path('schedule/', field_views.field_schedule, name='portal-field-schedule'),
    path('jobs/<job_no:number>/', field_views.field_job, name='portal-field-job'),
    path('jobs/<job_no:number>/print/', field_views.field_print, name='portal-field-print'),
    path('products/', field_views.field_products, name='portal-field-products'),
]
