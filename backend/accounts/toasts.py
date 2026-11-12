from django.contrib import messages


def greet_name(user) -> str:
    first = str(getattr(user, 'first_name', '') or '').strip()
    last = str(getattr(user, 'last_name', '') or '').strip()
    full = ' '.join(part for part in (first, last) if part)
    return full or user.get_username()


def queue_toast(request, text: str) -> str:
    text = str(text or '').strip()
    if text:
        messages.success(request, text)
    return text
