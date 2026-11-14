from django.urls import include, path

from . import notification_views, portal, views_search

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
    path('notifications/', notification_views.notifications_page, name='portal-notifications'),
    path('notifications/summary/', notification_views.notifications_summary, name='portal-notifications-summary'),
    path('notifications/read/', notification_views.notifications_read, name='portal-notifications-read'),
    path('notifications/push/', notification_views.push_subscription, name='portal-push-subscription'),
    path('search/', views_search.search_json, name='portal-search'),
    path('signout/', portal.portal_logout, name='portal-logout'),
    path('logo.png', portal.portal_logo, name='portal-logo'),
    path('favicon.ico', portal.portal_favicon, name='portal-favicon'),
    path('manifest.webmanifest', portal.portal_manifest, name='portal-manifest'),
    path('icons/<slug:name>.png', portal.portal_icon, name='portal-icon'),
    path('sw.js', portal.portal_service_worker, name='portal-service-worker'),
]
