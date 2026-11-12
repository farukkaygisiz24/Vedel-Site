from io import BytesIO
from pathlib import Path

from django.http import HttpResponse
from fpdf import FPDF

from accounts.portal import LOGO_PATH
from accounts.templatetags.portal_fmt import tr_money, tr_qty

FONT_DIR = Path(__file__).resolve().parent.parent / 'accounts' / 'static' / 'portal' / 'fonts'
FONT_REG = FONT_DIR / 'DejaVuSans.ttf'
FONT_BOLD = FONT_DIR / 'DejaVuSans-Bold.ttf'
VEDEL = (31, 74, 68)
INK = (29, 29, 31)
MUTED = (110, 110, 115)
LINE = (210, 210, 214)
LEFT = 14
RIGHT = 196
WIDTH = RIGHT - LEFT

COMPANY = {
    'unvan': 'Vedel Klima LTD. ŞTİ.',
    'merkez': '30 Ağustos Zafer Mah. Bozyaka Cad. No:11CA Nilüfer/Bursa',
    'sube': 'Altınşehir Mah. Uğur Mumcu Blv. No:58/E Nilüfer/Bursa',
    'vergi_dairesi': 'Çekirge V.D.',
    'vkn': '9240420644',
    'email': 'vedel@vedel.com.tr',
    'phone': '0224 413 23 16 - 17',
}

SERVICE = {
    'yetkili': 'Ömer Faruk Kaygısız',
    'phone': '0554 571 69 84',
}


class SaleFisPdf(FPDF):
    def __init__(self, sale):
        super().__init__(format='A4', unit='mm')
        self.sale = sale
        self.set_auto_page_break(auto=True, margin=18)
        self.add_font('DejaVu', '', str(FONT_REG))
        self.add_font('DejaVu', 'B', str(FONT_BOLD))
        self.set_margins(LEFT, 12, 14)

    def header(self):
        if self.page_no() > 1:
            self.set_font('DejaVu', 'B', 8)
            self.set_text_color(*VEDEL)
            self.cell(WIDTH - 50, 6, 'VEDEL KLİMA LTD. ŞTİ.')
            self.cell(50, 6, self.sale.number, align='R')
            self.ln(8)

    def footer(self):
        self.set_y(-14)
        self.set_draw_color(*LINE)
        self.set_line_width(0.2)
        self.line(LEFT, self.get_y(), RIGHT, self.get_y())
        self.set_font('DejaVu', '', 7.5)
        self.set_text_color(*MUTED)
        self.cell(WIDTH - 30, 6, f'{self.sale.number}  ·  {COMPANY["unvan"]}')
        self.cell(30, 6, str(self.page_no()), align='R')


def _rule(pdf, color=VEDEL, weight=0.45):
    y = pdf.get_y()
    pdf.set_draw_color(*color)
    pdf.set_line_width(weight)
    pdf.line(LEFT, y, RIGHT, y)
    pdf.ln(3)


def _kicker(pdf, text, align='L'):
    pdf.set_font('DejaVu', 'B', 7)
    pdf.set_text_color(*VEDEL)
    pdf.cell(WIDTH, 5, text.upper(), align=align)
    pdf.ln(5)


def _vat_heading(lines) -> str:
    rates = sorted({line.vat_rate for line in lines})
    if not rates:
        return 'KDV %20'
    if len(rates) == 1:
        return f'KDV %{tr_qty(rates[0])}'
    return 'KDV ' + ' / '.join(f'%{tr_qty(rate)}' for rate in rates)


def _totals_block(pdf, sale, lines):
    rows = [
        ('Ara toplam', f'{tr_money(sale.subtotal)} ₺', False),
        (_vat_heading(lines), f'{tr_money(sale.vat_total)} ₺', False),
        ('Genel toplam', f'{tr_money(sale.grand_total)} ₺', True),
    ]
    label_w, value_w = 46, 38
    x = LEFT + WIDTH - label_w - value_w
    pdf.ln(1)
    for label, value, strong in rows:
        pdf.set_x(x)
        pdf.set_font('DejaVu', 'B' if strong else '', 8.6 if strong else 8.2)
        pdf.set_text_color(*INK if strong else MUTED)
        pdf.cell(label_w, 5.6, label)
        pdf.set_font('DejaVu', 'B', 9 if strong else 8.4)
        pdf.set_text_color(*INK)
        pdf.cell(value_w, 5.6, value, align='R')
        pdf.ln(5.6)
    pdf.ln(3)


def _service_block(pdf):
    _kicker(pdf, 'Yetkili servis')
    _two_col(
        pdf,
        [
            ('Servis yetkilisi', SERVICE['yetkili']),
            ('Servis yetkili telefon no', SERVICE['phone']),
        ],
    )


def _line_kv(pdf, label, value, width=WIDTH):
    x, y = pdf.get_x(), pdf.get_y()
    pdf.set_font('DejaVu', 'B', 6.6)
    pdf.set_text_color(*MUTED)
    pdf.set_xy(x, y)
    pdf.cell(width, 3.6, label.upper())
    pdf.set_xy(x, y + 3.6)
    pdf.set_font('DejaVu', '', 8.5)
    pdf.set_text_color(*INK)
    pdf.multi_cell(width, 4.1, value or '—')


def _spread_row(pdf, cells, *, height=6, header=False):
    y = pdf.get_y()
    x = LEFT
    count = len(cells)
    pdf.set_font('DejaVu', 'B' if header else '', 7 if header else 8.4)
    pdf.set_text_color(*(MUTED if header else INK))
    for index, (text, align) in enumerate(cells):
        width = (LEFT + WIDTH) - x if index == count - 1 else WIDTH / count
        pdf.set_xy(x, y)
        pdf.cell(width, height, text.upper() if header else text, border='B', align=align)
        x += width
    pdf.set_y(y + height)


def _two_col(pdf, pairs):
    col_w = WIDTH / 2
    index = 0
    while index < len(pairs):
        y = pdf.get_y()
        pdf.set_xy(LEFT, y)
        _line_kv(pdf, pairs[index][0], pairs[index][1], col_w - 4)
        y_left = pdf.get_y()
        if index + 1 < len(pairs):
            pdf.set_xy(LEFT + col_w, y)
            _line_kv(pdf, pairs[index + 1][0], pairs[index + 1][1], col_w - 4)
            pdf.set_y(max(y_left, pdf.get_y()) + 1.4)
        else:
            pdf.set_y(y_left + 1.4)
        index += 2


def build_sale_pdf(sale) -> bytes:
    party = sale.party
    lines = list(sale.lines.select_related('product'))
    allocations = list(
        sale.payment_allocations.select_related('payment', 'payment__created_by').order_by(
            '-payment__date',
            '-id',
        )
    )
    pdf = SaleFisPdf(sale)
    pdf.add_page()
    y0 = 12

    if LOGO_PATH.exists():
        pdf.image(str(LOGO_PATH), x=LEFT, y=y0, w=16)
    pdf.set_xy(LEFT + 18, y0)
    pdf.set_font('DejaVu', 'B', 12)
    pdf.set_text_color(*VEDEL)
    pdf.cell(112, 6, COMPANY['unvan'])
    pdf.set_font('DejaVu', 'B', 11)
    pdf.set_text_color(*INK)
    pdf.cell(52, 6, 'SATIŞ FİŞİ', align='R')
    pdf.set_xy(LEFT + 18, y0 + 6)
    pdf.set_font('DejaVu', '', 7.4)
    pdf.set_text_color(*MUTED)
    pdf.multi_cell(112, 3.6, f'Merkez: {COMPANY["merkez"]}')
    pdf.set_x(LEFT + 18)
    pdf.multi_cell(112, 3.6, f'Şube: {COMPANY["sube"]}')
    pdf.set_xy(LEFT + 130, y0 + 6)
    pdf.set_font('DejaVu', 'B', 10)
    pdf.set_text_color(*INK)
    pdf.cell(52, 5, sale.number, align='R')
    pdf.set_xy(LEFT + 130, y0 + 11)
    pdf.set_font('DejaVu', '', 8)
    pdf.set_text_color(*MUTED)
    pdf.cell(52, 4, sale.date.strftime('%d.%m.%Y'), align='R')
    pdf.set_xy(LEFT + 130, y0 + 15)
    pdf.cell(52, 4, sale.get_work_type_display(), align='R')
    pdf.set_xy(LEFT + 18, pdf.get_y() + 0.5)
    pdf.set_font('DejaVu', '', 7.4)
    pdf.set_text_color(*MUTED)
    pdf.multi_cell(
        164,
        3.6,
        (
            f'Vergi dairesi: {COMPANY["vergi_dairesi"]}   '
            f'VKN: {COMPANY["vkn"]}   '
            f'E-posta: {COMPANY["email"]}   '
            f'Tel: {COMPANY["phone"]}'
        ),
    )
    pdf.ln(1)
    _rule(pdf)

    _kicker(pdf, 'Müşteri bilgileri')
    pdf.set_font('DejaVu', 'B', 12)
    pdf.set_text_color(*INK)
    pdf.cell(WIDTH, 6, party.display_name)
    pdf.ln(6)
    pdf.set_font('DejaVu', '', 8)
    pdf.set_text_color(*MUTED)
    pdf.cell(WIDTH, 4, party.get_kind_display())
    pdf.ln(6)

    city = ' / '.join(part for part in [party.district, party.city] if part) or '—'
    if party.kind == party.KIND_LEGAL:
        yetkili = f'{party.first_name} {party.last_name}'.strip() or '—'
        _two_col(
            pdf,
            [
                ('Yetkili', yetkili),
                ('Telefon', party.phone),
                ('Vergi dairesi', party.tax_office or '—'),
                ('Vergi no', party.tax_no or '—'),
            ],
        )
    else:
        _two_col(
            pdf,
            [
                ('T.C. kimlik no', party.national_id or '—'),
                ('Telefon', party.phone),
            ],
        )

    _kicker(pdf, '2. ulaşım')
    _two_col(
        pdf,
        [
            ('Ad soyad', party.contact2_name or '—'),
            ('Telefon', party.phone2 or '—'),
        ],
    )
    _two_col(
        pdf,
        [
            ('E-posta', party.email or '—'),
            ('İl / İlçe', city),
        ],
    )
    pdf.set_x(LEFT)
    _line_kv(pdf, 'Adres', (party.address or '—').replace('\n', ' '))
    pdf.ln(1)
    _rule(pdf, LINE, 0.25)

    _kicker(pdf, 'Kalemler')
    pdf.set_draw_color(*LINE)
    pdf.set_line_width(0.2)
    headers = [('Ürün', 78), ('Adet', 18), ('Birim', 30), ('KDV', 18), ('Tutar', 34)]
    pdf.set_font('DejaVu', 'B', 7)
    pdf.set_text_color(*MUTED)
    for title, width in headers:
        pdf.cell(width, 6.5, title.upper(), border='B', align='R' if title != 'Ürün' else 'L')
    pdf.ln(6.5)
    pdf.set_font('DejaVu', '', 8.4)
    pdf.set_text_color(*INK)
    for line in lines:
        name = line.display_name
        if line.description and line.product_id and line.description != line.product.display_name:
            name = f'{name} — {line.description}'
        pdf.cell(78, 6.5, name[:52], border='B')
        pdf.cell(18, 6.5, tr_qty(line.qty), border='B', align='R')
        pdf.cell(30, 6.5, f'{tr_money(line.unit_price)} ₺', border='B', align='R')
        pdf.cell(18, 6.5, f'%{tr_qty(line.vat_rate)}', border='B', align='R')
        pdf.cell(34, 6.5, f'{tr_money(line.line_total)} ₺', border='B', align='R')
        pdf.ln(6.5)

    _totals_block(pdf, sale, lines)

    notes = (sale.notes or '').strip()
    if notes:
        _kicker(pdf, 'İşlem notu')
        pdf.set_font('DejaVu', '', 8.5)
        pdf.set_text_color(*INK)
        pdf.multi_cell(WIDTH, 4.2, notes)
        pdf.ln(2)

    _service_block(pdf)
    _rule(pdf, LINE, 0.25)

    _kicker(pdf, 'Ödemeler')
    if allocations:
        _spread_row(
            pdf,
            [('Tarih', 'L'), ('Yöntem', 'L'), ('Tutar', 'L'), ('İşleyen', 'R')],
            header=True,
        )
        for alloc in allocations:
            pay = alloc.payment
            _spread_row(
                pdf,
                [
                    (pay.date.strftime('%d.%m.%Y'), 'L'),
                    (pay.get_method_display(), 'L'),
                    (f'{tr_money(alloc.amount)} ₺', 'L'),
                    (pay.created_by.username, 'R'),
                ],
            )
        card_pays = [
            (alloc, alloc.payment)
            for alloc in allocations
            if alloc.payment.method == alloc.payment.METHOD_CARD
            and (alloc.payment.card_holder or alloc.payment.card_installments)
        ]
        if card_pays:
            pdf.ln(3)
            _kicker(pdf, 'Mail order')
            for alloc, pay in card_pays:
                rows = [
                    ('Kart sahibi', pay.card_holder or '—'),
                    ('Taksit', pay.installment_label or '—'),
                    ('Tutar', f'{tr_money(alloc.amount)} ₺'),
                    ('Tarih', pay.date.strftime('%d.%m.%Y')),
                ]
                if pay.monthly_installment is not None:
                    rows.append(('Aylık taksit', f'{tr_money(pay.monthly_installment)} ₺'))
                _two_col(pdf, rows)
        transfer_pays = [
            (alloc, alloc.payment)
            for alloc in allocations
            if alloc.payment.method == alloc.payment.METHOD_TRANSFER and alloc.payment.transfer_sender
        ]
        if transfer_pays:
            pdf.ln(3)
            _kicker(pdf, 'Havale')
            for alloc, pay in transfer_pays:
                _two_col(
                    pdf,
                    [
                        ('Havale eden', pay.transfer_sender or '—'),
                        ('Tutar', f'{tr_money(alloc.amount)} ₺'),
                        ('Tarih', pay.date.strftime('%d.%m.%Y')),
                    ],
                )
    else:
        pdf.set_font('DejaVu', '', 8.5)
        pdf.set_text_color(*MUTED)
        pdf.cell(WIDTH, 6, 'Tahsilat yok.')
        pdf.ln(6)

    buf = BytesIO()
    pdf.output(buf)
    return buf.getvalue()


def sale_pdf_response(sale, *, download: bool = False) -> HttpResponse:
    payload = build_sale_pdf(sale)
    filename = f'{sale.number}.pdf'
    response = HttpResponse(payload, content_type='application/pdf')
    disposition = 'attachment' if download else 'inline'
    response['Content-Disposition'] = f'{disposition}; filename="{filename}"'
    response['Cache-Control'] = 'private, no-store'
    return response
