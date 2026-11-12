from django.urls import include, path

from . import portal

urlpatterns = [
    path('', portal.portal_login, name='portal-login'),
    path('login/', portal.portal_login, name='portal-login-alias'),
    path('account/', portal.portal_home, name='portal-home'),
    path('dashboard/', portal.portal_dashboard, name='portal-dashboard'),
    path('dashboard/settings/', portal.portal_settings, name='portal-settings'),
    path('service/', include('service.urls')),
    path('field/', include('service.field_urls')),
    path('sales/', include('sales.urls')),
    path('stock/', include('stock.urls')),
    path('crew/', include('crew.urls')),
    path('users/', include('accounts.user_urls')),
    path('signout/', portal.portal_logout, name='portal-logout'),
    path('logo.png', portal.portal_logo, name='portal-logo'),
    path('favicon.ico', portal.portal_favicon, name='portal-favicon'),
    path('manifest.webmanifest', portal.portal_manifest, name='portal-manifest'),
]
