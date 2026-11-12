from django.urls import path, register_converter

from . import views


class SaleNumberConverter:
    regex = r'[sS][aA][lL][0-9]{8,}'

    def to_python(self, value):
        return str(value).upper()

    def to_url(self, value):
        return ''.join(ch for ch in str(value).lower() if ch.isalnum())


class PartyNumberConverter:
    regex = r'[cC][uU][sS][tT][cC][0-9]{1,11}(?:-[0-9]+)?'

    def to_python(self, value):
        return str(value).upper()

    def to_url(self, value):
        return str(value).lower()


register_converter(SaleNumberConverter, 'sale_no')
register_converter(PartyNumberConverter, 'party_no')

urlpatterns = [
    path('', views.sale_list, name='portal-sales'),
    path('new/', views.sale_new, name='portal-sales-new'),
    path('archive/', views.sale_archive, name='portal-sales-archive'),
    path('archive/<sale_no:number>/', views.sale_archive_detail, name='portal-sales-archive-detail'),
    path('customers/', views.customer_list, name='portal-sales-customers'),
    path('customers/<int:pk>/', views.customer_detail_redirect),
    path('customers/<party_no:number>/', views.customer_edit, name='portal-sales-customers-edit'),
    path('<int:pk>/', views.sale_detail_redirect),
    path('<sale_no:number>/', views.sale_detail, name='portal-sales-detail'),
]
