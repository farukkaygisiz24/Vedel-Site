from django.urls import path, register_converter

from . import views


class CrewNumberConverter:
    regex = r'[pP][eE][rR]-[0-9]+'

    def to_python(self, value):
        return str(value).upper()

    def to_url(self, value):
        return str(value).lower()


register_converter(CrewNumberConverter, 'crew_no')

urlpatterns = [
    path('', views.crew_list, name='portal-crew'),
    path('new/', views.crew_new, name='portal-crew-new'),
    path('<crew_no:number>/', views.crew_item, name='portal-crew-item'),
]
