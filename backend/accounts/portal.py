from pathlib import Path

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_http_methods

from accounts.http import home_path, home_url_name, uses_field_app
from accounts.models import Customer
from accounts.toasts import greet_name, queue_toast
from accounts.weather import get_weather


def _wants_json(request: HttpRequest) -> bool:
    accept = request.headers.get('Accept', '')
    return 'application/json' in accept

LOGO_PATH = Path(__file__).resolve().parent / 'static' / 'portal' / 'vedel-logo.png'
FAVICON_PATH = Path(__file__).resolve().parent / 'static' / 'portal' / 'favicon.ico'


@require_http_methods(['GET', 'POST'])
def portal_login(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect(home_url_name(request.user))

    error = ''
    username = ''
    if request.method == 'POST':
        username = str(request.POST.get('username', '')).strip().lower()
        password = str(request.POST.get('password', ''))
        stored = Customer.objects.filter(username__iexact=username).only('username').first()
        user = authenticate(
            request,
            username=stored.username if stored else username,
            password=password,
        )
        if user is not None and user.is_active:
            login(request, user)
            queue_toast(request, f'Merhaba {greet_name(user)}')
            if _wants_json(request):
                return JsonResponse(
                    {
                        'ok': True,
                        'redirect': home_path(user),
                        'field': uses_field_app(user),
                        'username': user.get_username(),
                    }
                )
            return redirect(home_url_name(user))
        error = 'Kullanıcı adı veya şifre hatalı.'
        if _wants_json(request):
            return JsonResponse({'ok': False, 'error': error}, status=400)

    return render(
        request,
        'portal/login.html',
        {'error': error, 'username': username, 'weather': get_weather()},
    )


@login_required
def portal_home(request: HttpRequest) -> HttpResponse:
    return redirect(home_url_name(request.user))


@login_required
def portal_dashboard(request: HttpRequest) -> HttpResponse:
    home = home_url_name(request.user)
    if home != 'portal-dashboard':
        return redirect(home)
    from accounts.dashboard import dashboard_context

    ctx = dashboard_context(request.user)
    ctx['weather'] = get_weather()
    return render(request, 'portal/dashboard.html', ctx)


@login_required
@require_http_methods(['GET', 'POST'])
def portal_settings(request: HttpRequest) -> HttpResponse:
    user = request.user
    error = ''
    email = user.email
    phone = user.phone

    if request.method == 'POST':
        email = str(request.POST.get('email', '')).strip()
        phone = str(request.POST.get('phone', '')).strip()
        current_password = str(request.POST.get('current_password', ''))
        new_password = str(request.POST.get('new_password', ''))
        user.email = email
        user.phone = phone
        if new_password:
            if not current_password or not user.check_password(current_password):
                error = 'Mevcut şifre hatalı.'
            elif len(new_password) < 8:
                error = 'Yeni şifre en az 8 karakter olmalı.'
            else:
                user.set_password(new_password)
        if not error:
            user.save()
            if new_password:
                login(request, user)
            queue_toast(request, 'Ayarlar kaydedildi.')

    return render(
        request,
        'portal/field_settings.html' if uses_field_app(user) else 'portal/settings.html',
        {
            'weather': get_weather(),
            'email': email,
            'phone': phone,
            'error': error,
        },
    )


def portal_logout(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect('portal-login')


@require_GET
def portal_manifest(request: HttpRequest) -> JsonResponse:
    start = reverse('portal-login')
    if request.user.is_authenticated:
        start = home_path(request.user)
    response = JsonResponse(
        {
            'id': '/',
            'name': 'Vedel Servis',
            'short_name': 'Vedel',
            'lang': 'tr',
            'display': 'standalone',
            'display_override': ['standalone'],
            'orientation': 'portrait',
            'start_url': start,
            'scope': '/',
            'theme_color': '#eeecea',
            'background_color': '#eeecea',
            'icons': [
                {
                    'src': reverse('portal-logo'),
                    'type': 'image/png',
                    'sizes': '192x192',
                    'purpose': 'any',
                },
                {
                    'src': reverse('portal-favicon'),
                    'type': 'image/png',
                    'sizes': '32x32',
                    'purpose': 'any',
                },
            ],
        }
    )
    response['Content-Type'] = 'application/manifest+json'
    return response


@require_GET
def portal_logo(_request: HttpRequest) -> FileResponse:
    return FileResponse(LOGO_PATH.open('rb'), content_type='image/png')


@require_GET
def portal_favicon(_request: HttpRequest) -> FileResponse:
    return FileResponse(FAVICON_PATH.open('rb'), content_type='image/png')
