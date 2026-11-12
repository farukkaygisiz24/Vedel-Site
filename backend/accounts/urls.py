from django.urls import path

from . import views

urlpatterns = [
    path('health', views.health),
    path('health/', views.health),
    path('auth/register', views.register),
    path('auth/register/', views.register),
    path('auth/login', views.login_view),
    path('auth/login/', views.login_view),
    path('auth/logout', views.logout_view),
    path('auth/logout/', views.logout_view),
    path('auth/me', views.me),
    path('auth/me/', views.me),
]
