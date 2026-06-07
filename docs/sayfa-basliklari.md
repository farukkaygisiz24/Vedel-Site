# Sayfa Başlıkları (SEO / Sekme)

Bu doküman, sitedeki her sayfanın tarayıcı sekmesinde ve sosyal medyada görünen başlığını listeler.

## Nasıl çalışır?

`src/app/layout.tsx` içinde global şablon tanımlı:

```
template: "%s | VEDEL Klima"
```

Her sayfa **kısa başlık** verir; sistem otomatik olarak sonuna `| VEDEL Klima` ekler.

| Alan | Kullanım |
|------|----------|
| `metadata.title` | Kısa başlık → sekmede `{kısa} \| VEDEL Klima` |
| `openGraph.title` | Tam başlık (genelde `{kısa} \| VEDEL Klima`) |
| `layout default` | Ana sayfa; şablon uygulanmaz |

Yardımcı fonksiyonlar: `src/lib/metadata.ts` → `tabTitle()`, `fullTitle()`

---

## Statik sayfalar

| URL | Sekme başlığı | metadata.title (kısa) |
|-----|---------------|------------------------|
| `/` | Bursa Mitsubishi Heavy Industries Yetkili Bayi \| Vedel Klima | *(layout default)* |
| `/hakkimizda` | Hakkımızda \| VEDEL Klima | `Hakkımızda` |
| `/iletisim` | İletişim \| VEDEL Klima | `İletişim` |
| `/klimani-sec` | Klimanı Seç \| VEDEL Klima | `Klimanı Seç` |
| `/gizlilik-politikasi` | Gizlilik Politikası \| VEDEL Klima | `Gizlilik Politikası` |
| `/kvkk` | KVKK Aydınlatma Metni \| VEDEL Klima | `KVKK Aydınlatma Metni` |
| `/cerez-politikasi` | Çerez Politikası \| VEDEL Klima | `Çerez Politikası` |

---

## Ürün hub sayfaları

| URL | Sekme başlığı | metadata.title (kısa) |
|-----|---------------|------------------------|
| `/urunler/splitsistemler` | Split Sistem Klimalar \| MHI & Euroform \| VEDEL Klima | `Split Sistem Klimalar \| MHI & Euroform` |
| `/urunler/multisistemler` | Multi Sistem Klimalar \| Tek Dış Ünite Birden Fazla İç Ünite \| VEDEL Klima | `Multi Sistem Klimalar \| Tek Dış Ünite Birden Fazla İç Ünite` |
| `/urunler/profesyonelsistemler` | Profesyonel Klima Sistemleri \| Ticari İklimlendirme \| VEDEL Klima | `Profesyonel Klima Sistemleri \| Ticari İklimlendirme` |
| `/urunler/vrfsistemler` | VRF Sistemler \| Variable Refrigerant Flow \| VEDEL Klima | `VRF Sistemler \| Variable Refrigerant Flow` |

---

## Marka listeleme sayfaları (dinamik)

| URL | Sekme başlığı |
|-----|---------------|
| `/urunler/splitsistemler/mhi` | MHI Split Klimalar \| Mitsubishi Heavy Industries \| VEDEL Klima |
| `/urunler/splitsistemler/euroform` | Euroform Split Klimalar \| Wing Serisi \| VEDEL Klima |
| `/urunler/multisistemler/mhi` | MHI Multi Split Klimalar \| Tek Dış Ünite \| VEDEL Klima |
| `/urunler/multisistemler/euroform` | Euroform Multi Split Klimalar \| Ev ve İşyeri \| VEDEL Klima |
| `/urunler/profesyonelsistemler/mhi` | MHI Profesyonel Klimalar \| Ticari İklimlendirme \| VEDEL Klima |
| `/urunler/profesyonelsistemler/euroform` | Euroform Profesyonel Klimalar \| Endüstriyel Çözümler \| VEDEL Klima |

---

## Diğer ürün sayfaları

| URL | Sekme başlığı |
|-----|---------------|
| `/urunler/multisistemler/mhi/hesaplayici` | Multi Sistem Hesaplayıcı \| VEDEL Klima | `Multi Sistem Hesaplayıcı` |
| `/404` (not-found) | Sayfa Bulunamadı \| VEDEL Klima | `Sayfa Bulunamadı` |
| `/urunler/[brand]/[model]` | `{Ürün adı} {Model} \| {Marka} \| VEDEL Klima` |

**Ürün detay örneği:**  
`/urunler/mhi/SRK25ZSP-W` → `Trend Serisi SRK25ZSP-W | Mitsubishi Heavy Industries | VEDEL Klima`

---

## Düzenleme rehberi

1. Yeni sayfa eklerken `title: 'Sayfa Adı | VEDEL Klima'` **yazma** — çift suffix olur.
2. Doğru kullanım:
   ```ts
   import { tabTitle, fullTitle } from '@/lib/metadata'

   export const metadata = {
     title: tabTitle('Hakkımızda'),
     openGraph: { title: fullTitle('Hakkımızda') },
   }
   ```
3. Ana sayfa başlığını değiştirmek için `layout.tsx` → `title.default`.
4. Site adı suffix'ini değiştirmek için `layout.tsx` → `title.template`.

---

## Bilinen farklar

- Ana sayfa default'ta artık `VEDEL Klima` ile tutarlı.
- Uzun hub başlıkları sekmede kesilebilir; kısaltmak için sadece `metadata.title` alanını değiştir.
