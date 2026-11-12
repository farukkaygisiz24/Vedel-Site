from django.urls import path, register_converter

from . import user_views


class UsernameConverter:
    regex = r'[A-Za-z0-9._-]{3,32}'

    def to_python(self, value):
        return str(value)

    def to_url(self, value):
        return str(value)


register_converter(UsernameConverter, 'username')

urlpatterns = [
    path('', user_views.user_list, name='portal-users'),
    path('new/', user_views.user_new, name='portal-users-new'),
    path('<username:username>/', user_views.user_item, name='portal-users-item'),
]
