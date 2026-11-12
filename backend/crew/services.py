import re
from datetime import date, timedelta
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.http import FileResponse, Http404
from django.utils import timezone

from accounts.models import Customer
from sales.services import format_tr_phone, only_digits, tr_upper
from stock.services import pretty_label

from .models import CrewDocument, CrewMember

CREW_PREFIX = 'PER'
CREW_RE = re.compile(r'^PER-(\d+)$')
DOC_WINDOW_DAYS = 14
DOC_MAX_BYTES = 10 * 1024 * 1024
DOC_EXTS = {'.pdf', '.jpg', '.jpeg', '.png', '.webp', '.heic', '.doc', '.docx'}
MEMBER_FIELDS = (
    'first_name',
    'last_name',
    'national_id',
    'title',
    'phone',
    'phone2',
    'email',
    'address',
    'city',
    'district',
    'notes',
    'printer_mac',
    'printer_ip',
)
MAC_RE = re.compile(r'^[0-9A-F]{12}$')
IP_RE = re.compile(
    r'^(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)$'
)


def compact_crew_number(number: str) -> str:
    return re.sub(r'[^A-Za-z0-9-]', '', str(number or '')).upper()


def next_crew_number() -> str:
    serial = 0
    for number in CrewMember.objects.values_list('number', flat=True):
        match = CREW_RE.match(compact_crew_number(number))
        if match:
            serial = max(serial, int(match.group(1)))
    return f'{CREW_PREFIX}-{serial + 1:04d}'


def parse_expiry(raw) -> date:
    text = str(raw or '').strip()
    if not text:
        raise ValueError('Son tarih zorunlu.')
    try:
        return date.fromisoformat(text)
    except ValueError as exc:
        raise ValueError('Son tarih geçersiz.') from exc


def parse_national_id(raw) -> str:
    digits = only_digits(raw)
    if not digits:
        raise ValueError('T.C. kimlik no zorunlu.')
    if len(digits) != 11:
        raise ValueError('T.C. kimlik no 11 haneli olmalıdır.')
    return digits


def parse_printer_mac(raw) -> str:
    text = str(raw or '').strip().upper().replace('-', ':')
    if not text:
        return ''
    hex_only = re.sub(r'[^0-9A-F]', '', text)
    if not MAC_RE.match(hex_only):
        raise ValueError('Yazıcı MAC 12 haneli olmalıdır.')
    return ':'.join(hex_only[i:i + 2] for i in range(0, 12, 2))


def parse_printer_ip(raw) -> str:
    text = str(raw or '').strip()
    if not text:
        return ''
    if not IP_RE.match(text):
        raise ValueError('Yazıcı IP geçersiz.')
    return text


def parse_email(raw) -> str:
    text = str(raw or '').strip()
    if not text:
        return ''
    try:
        validate_email(text)
    except ValidationError as exc:
        raise ValueError('E-posta geçersiz.') from exc
    return text


def member_form_values(member: CrewMember | None = None, post=None) -> dict:
    if post is not None:
        return {key: str(post.get(key, '')) for key in MEMBER_FIELDS}
    if member is None:
        return {key: '' for key in MEMBER_FIELDS}
    return {key: getattr(member, key) or '' for key in MEMBER_FIELDS}


def posted_document_rows(post, *, today: date | None = None) -> list[dict]:
    titles = post.getlist('doc_title') if hasattr(post, 'getlist') else []
    dates = post.getlist('doc_expires_on') if hasattr(post, 'getlist') else []
    fallback = (today or timezone.localdate()).isoformat()
    count = max(len(titles), len(dates), 1)
    rows = []
    for index in range(count):
        rows.append({
            'title': titles[index] if index < len(titles) else '',
            'expires_on': dates[index] if index < len(dates) else fallback,
        })
    return rows


def parse_upload(upload):
    if not upload or not getattr(upload, 'size', 0):
        raise ValueError('Evrak için dosya seçin.')
    if upload.size > DOC_MAX_BYTES:
        raise ValueError('Evrak en fazla 10 MB olabilir.')
    name = Path(str(upload.name or '')).name
    ext = Path(name).suffix.lower()
    if ext not in DOC_EXTS:
        raise ValueError('Evrak PDF, görsel veya Word dosyası olmalı.')
    return upload, name[:200]


def documents_from_post(post, files) -> list[dict]:
    titles = post.getlist('doc_title')
    dates = post.getlist('doc_expires_on')
    raw_files = files.getlist('doc_file') if files is not None and hasattr(files, 'getlist') else []
    uploads = [item for item in raw_files if item and getattr(item, 'size', 0)]
    parsed = []
    upload_index = 0
    count = max(len(titles), len(dates))
    for index in range(count):
        title = pretty_label(titles[index] if index < len(titles) else '')
        raw = dates[index] if index < len(dates) else ''
        if not title:
            continue
        if upload_index >= len(uploads):
            raise ValueError('Her evrak için dosya yükleyin.')
        upload, original = parse_upload(uploads[upload_index])
        upload_index += 1
        parsed.append({
            'title': title,
            'upload': upload,
            'original_name': original,
            'expires_on': parse_expiry(raw),
        })
    if upload_index < len(uploads):
        raise ValueError('Dosya için evrak adı yazın.')
    return parsed


def member_from_post(post, user, member: CrewMember | None = None) -> CrewMember:
    first_name = pretty_label(post.get('first_name', ''))
    last_name = pretty_label(post.get('last_name', ''))
    if not first_name:
        raise ValueError('Ad zorunlu.')
    if not last_name:
        raise ValueError('Soyad zorunlu.')
    address = tr_upper(post.get('address', ''))
    if not address:
        raise ValueError('Ev adresi zorunlu.')
    if member is None:
        member = CrewMember(
            number=next_crew_number(),
            created_by=user,
        )
    member.first_name = first_name
    member.last_name = last_name
    member.national_id = parse_national_id(post.get('national_id', ''))
    member.phone = format_tr_phone(post.get('phone', ''), required=True)
    member.phone2 = format_tr_phone(post.get('phone2', ''), required=False)
    member.email = parse_email(post.get('email', ''))
    member.title = pretty_label(post.get('title', ''))
    member.address = address
    member.city = tr_upper(post.get('city', ''))
    member.district = tr_upper(post.get('district', ''))
    member.notes = str(post.get('notes', '')).strip()
    if 'printer_mac' in post:
        member.printer_mac = parse_printer_mac(post.get('printer_mac', ''))
    if 'printer_ip' in post:
        member.printer_ip = parse_printer_ip(post.get('printer_ip', ''))
    member.save()
    return member


def link_member_user(*, member: CrewMember, user: Customer) -> CrewMember:
    other = CrewMember.objects.filter(user=user).exclude(pk=member.pk).first()
    if other:
        raise ValueError('Bu kullanıcı başka personele bağlı.')
    member.user = user
    member.save(update_fields=['user', 'updated_at'])
    return member


@transaction.atomic
def save_member_access(*, member: CrewMember, post) -> CrewMember:
    member.printer_mac = parse_printer_mac(post.get('printer_mac', ''))
    member.printer_ip = parse_printer_ip(post.get('printer_ip', ''))
    member.save(update_fields=['printer_mac', 'printer_ip', 'updated_at'])
    return member


def _create_documents(*, member: CrewMember, user, rows: list[dict]) -> None:
    for item in rows:
        CrewDocument.objects.create(
            member=member,
            title=item['title'],
            original_name=item['original_name'],
            file=item['upload'],
            expires_on=item['expires_on'],
            created_by=user,
        )


@transaction.atomic
def create_member(*, user, post, files=None) -> CrewMember:
    member = member_from_post(post, user)
    _create_documents(member=member, user=user, rows=documents_from_post(post, files or {}))
    return member


@transaction.atomic
def update_member(*, member: CrewMember, user, post) -> CrewMember:
    member_from_post(post, user, member=member)
    return member


@transaction.atomic
def add_document(*, member: CrewMember, user, post, files=None) -> CrewDocument:
    title = pretty_label(post.get('title', ''))
    if not title:
        raise ValueError('Evrak adı zorunlu.')
    files = files or {}
    upload = files.get('file') or files.get('doc_file')
    stored, original = parse_upload(upload)
    return CrewDocument.objects.create(
        member=member,
        title=title,
        original_name=original,
        file=stored,
        expires_on=parse_expiry(post.get('expires_on')),
        created_by=user,
    )


@transaction.atomic
def delete_document(*, member: CrewMember, post) -> None:
    raw = str(post.get('document_id', '')).strip()
    if not raw.isdigit():
        raise ValueError('Evrak seçin.')
    doc = CrewDocument.objects.filter(pk=int(raw), member=member).first()
    if not doc:
        raise ValueError('Evrak bulunamadı.')
    doc.delete()


def reminder_bounds(today: date | None = None):
    today = today or timezone.localdate()
    return today, today + timedelta(days=DOC_WINDOW_DAYS)


def download_document(*, member: CrewMember, raw_id: str):
    if not str(raw_id).isdigit():
        raise Http404()
    doc = CrewDocument.objects.filter(pk=int(raw_id), member=member).first()
    if not doc or not doc.file:
        raise Http404()
    try:
        handle = doc.file.open('rb')
    except FileNotFoundError as exc:
        raise Http404() from exc
    filename = doc.original_name or Path(doc.file.name).name
    return FileResponse(handle, as_attachment=True, filename=filename)
