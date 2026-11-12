import json
import urllib.request
from datetime import date
from time import monotonic
from typing import Any
from urllib.error import URLError

CITY = 'Bursa'
LATITUDE = 40.211
LONGITUDE = 28.964
CACHE_SECONDS = 900
TIMEOUT_SECONDS = 1.8

DAY_NAMES = ['Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz']

_cache: dict[str, Any] = {'at': 0.0, 'data': None}


def _label_for_code(code: int) -> str:
    if code == 0:
        return 'Açık'
    if code in (1, 2):
        return 'Parçalı bulutlu'
    if code == 3:
        return 'Bulutlu'
    if code in (45, 48):
        return 'Sisli'
    if code in (51, 53, 55, 56, 57):
        return 'Çisenti'
    if code in (61, 63, 65, 66, 67, 80, 81, 82):
        return 'Yağmurlu'
    if code in (71, 73, 75, 77, 85, 86):
        return 'Karlı'
    if code in (95, 96, 99):
        return 'Fırtınalı'
    return 'Değişken'


def _icon_for_code(code: int) -> str:
    if code in (0, 1):
        return 'sun'
    if code == 2:
        return 'cloud-sun'
    if code in (3, 45, 48):
        return 'cloud'
    if code in (71, 73, 75, 77, 85, 86):
        return 'snow'
    if code in (95, 96, 99):
        return 'storm'
    return 'rain'


def _sky_for_code(code: int) -> str:
    if code in (0, 1):
        return 'sun'
    if code == 2:
        return 'cloud-sun'
    if code == 3:
        return 'cloud'
    if code in (45, 48):
        return 'fog'
    if code in (51, 53, 55, 56, 57):
        return 'drizzle'
    if code in (71, 73, 75, 77, 85, 86):
        return 'snow'
    if code in (95, 96, 99):
        return 'storm'
    return 'rain'


def _fetch() -> dict[str, Any] | None:
    query = (
        'https://api.open-meteo.com/v1/forecast'
        f'?latitude={LATITUDE}&longitude={LONGITUDE}'
        '&current=temperature_2m,apparent_temperature,relative_humidity_2m,'
        'weather_code,wind_speed_10m'
        '&daily=weather_code,temperature_2m_max,temperature_2m_min'
        '&timezone=Europe%2FIstanbul&forecast_days=5'
    )
    try:
        with urllib.request.urlopen(query, timeout=TIMEOUT_SECONDS) as response:
            payload = json.loads(response.read().decode('utf-8'))
    except (URLError, TimeoutError, ValueError, json.JSONDecodeError):
        return None

    current = payload.get('current') or {}
    daily = payload.get('daily') or {}
    code = int(current.get('weather_code') or 0)
    days = []
    times = daily.get('time') or []
    highs = daily.get('temperature_2m_max') or []
    lows = daily.get('temperature_2m_min') or []
    codes = daily.get('weather_code') or []
    today = date.today().isoformat()
    for index, day in enumerate(times[:5]):
        weekday = date.fromisoformat(day).weekday()
        days.append(
            {
                'name': 'Bugün' if day == today else DAY_NAMES[weekday],
                'icon': _icon_for_code(int(codes[index] if index < len(codes) else 0)),
                'max': round(float(highs[index] if index < len(highs) else 0)),
                'min': round(float(lows[index] if index < len(lows) else 0)),
            }
        )

    return {
        'city': CITY,
        'temp': round(float(current.get('temperature_2m') or 0)),
        'feels': round(float(current.get('apparent_temperature') or 0)),
        'humidity': round(float(current.get('relative_humidity_2m') or 0)),
        'wind': round(float(current.get('wind_speed_10m') or 0)),
        'label': _label_for_code(code),
        'icon': _icon_for_code(code),
        'sky': _sky_for_code(code),
        'days': days,
    }


def get_weather() -> dict[str, Any] | None:
    now = monotonic()
    cached = _cache['data']
    if cached is not None and now - float(_cache['at']) < CACHE_SECONDS:
        return cached

    fresh = _fetch()
    if fresh is not None:
        _cache['at'] = now
        _cache['data'] = fresh
        return fresh
    return cached
