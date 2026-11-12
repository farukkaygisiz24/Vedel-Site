from django.urls import path, register_converter

from . import views


class SkuConverter:
    regex = r'[a-zA-Z]{2,6}-[0-9]+'

    def to_python(self, value):
        return str(value).upper()

    def to_url(self, value):
        return str(value).lower()


register_converter(SkuConverter, 'sku_no')

urlpatterns = [
    path('', views.stock_home, name='portal-stock'),
    path('new/', views.product_new, name='portal-stock-new'),
    path('items/<sku_no:number>/', views.product_item, name='portal-stock-item'),
]
