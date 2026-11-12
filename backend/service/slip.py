from datetime import datetime

from accounts.templatetags.portal_fmt import tr_money

_TR_ASCII = str.maketrans('çğıöşüÇĞİÖŞÜ', 'cgiosuCGIOSU')


def _ascii_tr(text: str) -> str:
    return str(text or '').translate(_TR_ASCII)


def _cpcl_text(x: int, y: int, text: str, font: int = 7, size: int = 0) -> str:
    clean = _ascii_tr(text).replace('\r', ' ').replace('\n', ' ').strip()
    return f'TEXT {font} {size} {x} {y} {clean}'


def slip_context(job) -> dict:
    worker = job.assignee_label
    party = job.party.display_name if job.party_id else ''
    when = job.date.strftime('%d.%m.%Y')
    if job.time:
        when = f'{when} {job.time.strftime("%H:%M")}'
    lines = []
    for item in job.lines.all():
        lines.append({
            'name': item.description or item.get_kind_display(),
            'qty': str(item.qty).rstrip('0').rstrip('.') if item.qty else '1',
            'total': tr_money(item.line_total),
        })
    return {
        'job': job,
        'number': job.number,
        'worker': worker,
        'customer': party,
        'when': when,
        'notes': job.notes,
        'lines': lines,
        'grand': tr_money(job.grand_total),
        'printed_at': datetime.now().strftime('%d.%m.%Y %H:%M'),
    }


def build_job_slip_cpcl(job) -> bytes:
    data = slip_context(job)
    y = 20
    cmds = [
        '! 0 200 200 900 1',
        'CENTER',
        _cpcl_text(0, y, 'VEDEL KLIMA'),
    ]
    y += 36
    cmds.append('LEFT')
    cmds.append(_cpcl_text(10, y, data['number']))
    y += 28
    cmds.append(_cpcl_text(10, y, data['when']))
    y += 36
    cmds.append(_cpcl_text(10, y, 'Personel'))
    y += 24
    cmds.append(_cpcl_text(10, y, data['worker'] or '—'))
    y += 32
    cmds.append(_cpcl_text(10, y, 'Musteri'))
    y += 24
    cmds.append(_cpcl_text(10, y, data['customer'] or '—'))
    y += 36
    for item in data['lines'][:12]:
        cmds.append(_cpcl_text(10, y, item['name'][:28]))
        y += 22
        cmds.append(_cpcl_text(10, y, f"{item['qty']}  {item['total']} TL"))
        y += 26
    if data['lines']:
        cmds.append(_cpcl_text(10, y, f"Toplam  {data['grand']} TL"))
        y += 32
    cmds.append('FORM')
    cmds.append('PRINT')
    cmds.append('')
    body = '\r\n'.join(cmds)
    return body.encode('cp437', errors='replace')


def build_job_slip_zpl(job) -> bytes:
    data = slip_context(job)
    y = 40
    lines = [
        '^XA',
        '^CI28',
        '^PW576',
        '^LL900',
        f'^FO0,{y}^A0N,36,36^FDVEDEL KLIMA^FS',
    ]
    y += 48
    lines.append(f"^FO20,{y}^A0N,28,28^FD{_ascii_tr(data['number'])}^FS")
    y += 36
    lines.append(f"^FO20,{y}^A0N,24,24^FD{_ascii_tr(data['when'])}^FS")
    y += 40
    lines.append(f'^FO20,{y}^A0N,22,22^FDPersonel^FS')
    y += 28
    lines.append(f"^FO20,{y}^A0N,28,28^FD{_ascii_tr(data['worker'] or '-')}^FS")
    y += 40
    lines.append(f'^FO20,{y}^A0N,22,22^FDMusteri^FS')
    y += 28
    lines.append(f"^FO20,{y}^A0N,28,28^FD{_ascii_tr(data['customer'] or '-')}^FS")
    y += 44
    for item in data['lines'][:12]:
        lines.append(f"^FO20,{y}^A0N,24,24^FD{_ascii_tr(item['name'][:28])}^FS")
        y += 28
        lines.append(f"^FO20,{y}^A0N,22,22^FD{_ascii_tr(item['qty'])}  {_ascii_tr(item['total'])} TL^FS")
        y += 32
    if data['lines']:
        lines.append(f"^FO20,{y}^A0N,26,26^FDToplam  {_ascii_tr(data['grand'])} TL^FS")
    lines.append('^XZ')
    return '\n'.join(lines).encode('utf-8')
