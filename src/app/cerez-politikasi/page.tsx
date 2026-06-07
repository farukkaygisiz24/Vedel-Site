import type { Metadata } from 'next'
import LegalPageLayout from '@/components/legal/LegalPageLayout'

export const metadata: Metadata = {
  title: 'Çerez Politikası',
  description:
    'VEDEL Klima web sitesinde kullanılan çerezler ve tercihlerinizi nasıl yönetebileceğiniz hakkında bilgi.',
  openGraph: {
    type: 'website',
    locale: 'tr_TR',
    url: 'https://vedel.com.tr/cerez-politikasi',
    siteName: 'VEDEL Klima',
    title: 'Çerez Politikası',
    description: 'VEDEL Klima çerez kullanım politikası.',
  },
}

const sections = [
  {
    title: '1. Çerez Nedir?',
    content: (
      <>
        <p>
          Çerezler, web sitemizi ziyaret ettiğinizde cihazınıza kaydedilen küçük metin dosyalarıdır.
          Site deneyimini iyileştirmek, tercihlerinizi hatırlamak ve kullanım istatistikleri
          toplamak için kullanılır.
        </p>
      </>
    ),
  },
  {
    title: '2. Kullandığımız Çerez Türleri',
    content: (
      <>
        <div className="space-y-4">
          <div>
            <p className="font-semibold text-gray-800">Zorunlu Çerezler</p>
            <p>
              Sitenin temel işlevlerinin çalışması için gereklidir. Devre dışı bırakılamazlar.
              Örnek: oturum yönetimi, güvenlik.
            </p>
          </div>
          <div>
            <p className="font-semibold text-gray-800">Performans / Analitik Çerezler</p>
            <p>
              Ziyaretçi sayısı, hangi sayfaların görüntülendiği gibi anonim istatistikler
              toplar. Site performansını iyileştirmemize yardımcı olur.
            </p>
          </div>
          <div>
            <p className="font-semibold text-gray-800">Pazarlama / Reklam Çerezleri</p>
            <p>
              Google Ads gibi reklam platformları tarafından kullanılır. Reklam kampanyalarının
              etkinliğini ölçmek ve ilgili içerik sunmak amacıyla yerleştirilebilir.
            </p>
          </div>
          <div>
            <p className="font-semibold text-gray-800">Yerel Depolama (Local / Session Storage)</p>
            <p>
              Fiyat listesi gibi verileri geçici olarak tarayıcınızda saklamak için kullanılır
              (ör. <code className="rounded bg-gray-100 px-1.5 py-0.5 text-sm">vedel_prices</code>).
              Bu, sayfa yükleme hızını artırır.
            </p>
          </div>
        </div>
      </>
    ),
  },
  {
    title: '3. Üçüncü Taraf Çerezleri',
    content: (
      <>
        <p>Sitemizde aşağıdaki üçüncü taraf hizmetler çerez kullanabilir:</p>
        <ul className="list-disc space-y-2 pl-5">
          <li><strong>Google Ads</strong> — reklam dönüşüm takibi</li>
          <li><strong>Google Maps</strong> — iletişim sayfasındaki harita gömüleri</li>
        </ul>
        <p>
          Bu hizmetlerin çerez politikaları için ilgili sağlayıcıların web sitelerini
          inceleyebilirsiniz.
        </p>
      </>
    ),
  },
  {
    title: '4. Çerez Tercihlerinizi Yönetme',
    content: (
      <>
        <p>Çerez tercihlerinizi aşağıdaki yollarla yönetebilirsiniz:</p>
        <ul className="list-disc space-y-2 pl-5">
          <li>Tarayıcı ayarlarından çerezleri silme veya engelleme</li>
          <li>Tarayıcınızın &quot;Gizlilik&quot; veya &quot;Çerezler&quot; bölümünden tercihleri düzenleme</li>
          <li>Google reklam ayarları:{' '}
            <a href="https://adssettings.google.com" target="_blank" rel="noopener noreferrer">
              adssettings.google.com
            </a>
          </li>
        </ul>
        <p>
          Zorunlu olmayan çerezleri reddetmeniz halinde sitenin bazı özellikleri sınırlı
          çalışabilir; temel içerik ve ürün bilgilerine erişim devam eder.
        </p>
      </>
    ),
  },
  {
    title: '5. Saklama Süreleri',
    content: (
      <>
        <ul className="list-disc space-y-2 pl-5">
          <li>Oturum çerezleri: tarayıcı kapatılana kadar</li>
          <li>Kalıcı çerezler: birkaç gün ile 24 ay arasında (çerez türüne göre değişir)</li>
          <li>Fiyat önbelleği (sessionStorage): tarayıcı sekmesi kapatılana kadar</li>
        </ul>
      </>
    ),
  },
  {
    title: '6. İlgili Metinler',
    content: (
      <>
        <p>
          Kişisel verilerinizin işlenmesi hakkında daha fazla bilgi için{' '}
          <a href="/gizlilik-politikasi">Gizlilik Politikası</a> ve{' '}
          <a href="/kvkk">KVKK Aydınlatma Metni</a> sayfalarımıza bakınız.
        </p>
      </>
    ),
  },
]

export default function CerezPolitikasiPage() {
  return (
    <LegalPageLayout
      title="Çerez Politikası"
      subtitle="Web sitemizde hangi çerezleri kullandığımızı ve tercihlerinizi nasıl yönetebileceğinizi açıklıyoruz."
      lastUpdated="6 Haziran 2026"
      sections={sections}
    />
  )
}
