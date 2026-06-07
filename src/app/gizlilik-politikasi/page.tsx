import type { Metadata } from 'next'
import LegalPageLayout from '@/components/legal/LegalPageLayout'

export const metadata: Metadata = {
  title: 'Gizlilik Politikası',
  description:
    'VEDEL Klima gizlilik politikası. Kişisel verilerinizin nasıl toplandığı, kullanıldığı ve korunduğu hakkında bilgi.',
  openGraph: {
    type: 'website',
    locale: 'tr_TR',
    url: 'https://vedel.com.tr/gizlilik-politikasi',
    siteName: 'VEDEL Klima',
    title: 'Gizlilik Politikası',
    description: 'VEDEL Klima gizlilik politikası ve kişisel veri koruma uygulamaları.',
  },
}

const sections = [
  {
    title: '1. Giriş',
    content: (
      <>
        <p>
          Bu Gizlilik Politikası, Vedel Klima Ltd. Şti. (&quot;VEDEL Klima&quot;, &quot;biz&quot;) tarafından
          işletilen vedel.com.tr web sitesini ziyaret ettiğinizde kişisel verilerinizin nasıl
          toplandığını, kullanıldığını ve korunduğunu açıklar.
        </p>
        <p>
          Web sitemizi kullanarak bu politikada belirtilen uygulamaları kabul etmiş sayılırsınız.
          Detaylı bilgi için{' '}
          <a href="/kvkk">KVKK Aydınlatma Metni</a> sayfamızı da inceleyebilirsiniz.
        </p>
      </>
    ),
  },
  {
    title: '2. Veri Sorumlusu',
    content: (
      <>
        <p>
          <strong>Vedel Klima Ltd. Şti.</strong>
          <br />
          Kayapa Bayi: 30 Ağustos Zafer Mah. Bozyaka Cad. No:11/CA Nilüfer / Bursa
          <br />
          Özlüce Bayi: Altınşehir Mah. Uğur Mumcu Blv. No:58/E Nilüfer / Bursa
          <br />
          E-posta: vedel@vedel.com.tr
          <br />
          Telefon: (0224) 413 23 16
        </p>
      </>
    ),
  },
  {
    title: '3. Toplanan Veriler',
    content: (
      <>
        <p>Web sitemiz aracılığıyla aşağıdaki veriler toplanabilir:</p>
        <ul className="list-disc space-y-2 pl-5">
          <li>İletişim bilgileri (ad, soyad, telefon, e-posta) — bize ulaştığınızda</li>
          <li>Teknik veriler (IP adresi, tarayıcı türü, cihaz bilgisi, ziyaret edilen sayfalar)</li>
          <li>Çerezler ve benzeri teknolojiler aracılığıyla elde edilen kullanım verileri</li>
        </ul>
        <p>
          Ürün fiyatları Google Sheets üzerinden sunulmaktadır; bu süreçte kişisel veri
          toplanmaz, yalnızca anonim istek logları işlenebilir.
        </p>
      </>
    ),
  },
  {
    title: '4. Verilerin Kullanım Amaçları',
    content: (
      <>
        <ul className="list-disc space-y-2 pl-5">
          <li>İletişim taleplerinize yanıt vermek ve hizmet sunmak</li>
          <li>Web sitesinin işletilmesi, güvenliği ve performansının iyileştirilmesi</li>
          <li>Yasal yükümlülüklerin yerine getirilmesi</li>
          <li>Reklam ve pazarlama faaliyetlerinin ölçülmesi (onayınız dahilinde)</li>
        </ul>
      </>
    ),
  },
  {
    title: '5. Verilerin Paylaşımı',
    content: (
      <>
        <p>
          Kişisel verileriniz, yasal zorunluluklar ve hizmet sağlayıcılarımız (hosting, analitik,
          reklam platformları) dışında üçüncü taraflarla paylaşılmaz. Hizmet sağlayıcıları yalnızca
          belirlenen amaçlar doğrultusunda ve gerekli güvenlik önlemleriyle veri işler.
        </p>
      </>
    ),
  },
  {
    title: '6. Veri Güvenliği',
    content: (
      <>
        <p>
          Kişisel verilerinizi korumak için uygun teknik ve idari tedbirler alınmaktadır. Bununla
          birlikte, internet üzerinden yapılan hiçbir veri iletiminin %100 güvenli olmadığını
          hatırlatırız.
        </p>
      </>
    ),
  },
  {
    title: '7. Haklarınız',
    content: (
      <>
        <p>
          6698 sayılı Kişisel Verilerin Korunması Kanunu kapsamında verilerinize erişim, düzeltme,
          silme, işlemeyi kısıtlama ve itiraz etme haklarına sahipsiniz. Taleplerinizi{' '}
          <a href="mailto:vedel@vedel.com.tr">vedel@vedel.com.tr</a> adresine iletebilirsiniz.
        </p>
      </>
    ),
  },
  {
    title: '8. Politika Değişiklikleri',
    content: (
      <>
        <p>
          Bu politika zaman zaman güncellenebilir. Güncel sürüm her zaman bu sayfada yayımlanır.
          Önemli değişikliklerde web sitemiz üzerinden bilgilendirme yapılabilir.
        </p>
      </>
    ),
  },
]

export default function GizlilikPolitikasiPage() {
  return (
    <LegalPageLayout
      title="Gizlilik Politikası"
      subtitle="Kişisel verilerinizin korunması bizim için önemlidir. Bu sayfada verilerinizin nasıl işlendiğini bulabilirsiniz."
      lastUpdated="6 Haziran 2026"
      sections={sections}
    />
  )
}
