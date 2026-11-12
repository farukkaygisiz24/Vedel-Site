import json
import re

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import AuthToken, Customer

USERNAME_RE = re.compile(r'^[A-Za-z0-9._-]{3,32}$')


@require_GET
def health(_request):
    return JsonResponse({'ok': True, 'service': 'vedel-b2c'})


def _json_body(request):
    try:
        return json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return None


def _user_payload(user: Customer):
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'phone': user.phone,
    }


def _auth_user(request):
    header = request.headers.get('Authorization', '')
    if not header.startswith('Bearer '):
        return None
    key = header[7:].strip()
    if not key:
        return None
    token = (
        AuthToken.objects.select_related('user')
        .filter(key=key, user__is_active=True)
        .first()
    )
    return token.user if token else None


@csrf_exempt
@require_POST
def register(request):
    data = _json_body(request)
    if data is None:
        return JsonResponse({'error': 'Geçersiz istek.'}, status=400)

    username = str(data.get('username', '')).strip().lower()
    password = str(data.get('password', ''))
    password_confirm = str(data.get('password_confirm', password))
    email = str(data.get('email', '')).strip()
    phone = str(data.get('phone', '')).strip()

    if not USERNAME_RE.match(username):
        return JsonResponse(
            {
                'error': 'Kullanıcı adı 3-32 karakter olmalı; harf, rakam, nokta, tire ve alt çizgi kullanılabilir.',
            },
            status=400,
        )
    if password != password_confirm:
        return JsonResponse({'error': 'Şifreler eşleşmiyor.'}, status=400)
    if Customer.objects.filter(username__iexact=username).exists():
        return JsonResponse({'error': 'Bu kullanıcı adı alınmış.'}, status=400)

    user = Customer(username=username, email=email, phone=phone)
    try:
        validate_password(password, user=user)
    except ValidationError as exc:
        return JsonResponse({'error': ' '.join(exc.messages)}, status=400)

    user.set_password(password)
    user.save()
    token = AuthToken.issue(user)
    return JsonResponse({'token': token.key, 'user': _user_payload(user)}, status=201)


@csrf_exempt
@require_POST
def login_view(request):
    data = _json_body(request)
    if data is None:
        return JsonResponse({'error': 'Geçersiz istek.'}, status=400)

    username = str(data.get('username', '')).strip().lower()
    password = str(data.get('password', ''))
    stored = Customer.objects.filter(username__iexact=username).only('username').first()
    user = authenticate(
        request,
        username=stored.username if stored else username,
        password=password,
    )
    if user is None or not user.is_active:
        return JsonResponse({'error': 'Kullanıcı adı veya şifre hatalı.'}, status=400)

    token = AuthToken.issue(user)
    return JsonResponse({'token': token.key, 'user': _user_payload(user)})


@csrf_exempt
@require_POST
def logout_view(request):
    header = request.headers.get('Authorization', '')
    if header.startswith('Bearer '):
        AuthToken.objects.filter(key=header[7:].strip()).delete()
    return JsonResponse({'ok': True})


@require_GET
def me(request):
    user = _auth_user(request)
    if user is None:
        return JsonResponse({'error': 'Oturum bulunamadı.'}, status=401)
    return JsonResponse({'user': _user_payload(user)})
