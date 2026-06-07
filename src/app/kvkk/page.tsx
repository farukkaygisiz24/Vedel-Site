import type { Metadata } from 'next'
import LegalPageLayout from '@/components/legal/LegalPageLayout'

export const metadata: Metadata = {
  title: 'KVKK Aydınlatma Metni',
  description:
    'VEDEL Klima Kişisel Verilerin Korunması Kanunu (KVKK) kapsamında aydınlatma metni.',
  openGraph: {
    type: 'website',
    locale: 'tr_TR',
    url: 'https://vedel.com.tr/kvkk',
    siteName: 'VEDEL Klima',
    title: 'KVKK Aydınlatma Metni',
    description: 'VEDEL Klima KVKK aydınlatma metni ve kişisel veri işleme bilgileri.',
  },
}

const sections = [
  {
    title: '1. Veri Sorumlusu',
    content: (
      <>
        <p>
          6698 sayılı Kişisel Verilerin Korunması Kanunu (&quot;KVKK&quot;) uyarınca veri sorumlusu:
        </p>
        <p>
          <strong>Vedel Klima Ltd. Şti.</strong>
          <br />
          Kayapa Bayi: 30 Ağustos Zafer Mah. Bozyaka Cad. No:11/CA Nilüfer / Bursa
          <br />
          Özlüce Bayi: Altınşehir Mah. Uğur Mumcu Blv. No:58/E Nilüfer / Bursa
          <br />
          E-posta: <a href="mailto:vedel@vedel.com.tr">vedel@vedel.com.tr</a>
          <br />
          Telefon: (0224) 413 23 16
        </p>
      </>
    ),
  },
  {
    title: '2. İşlenen Kişisel Veriler',
    content: (
      <>
        <p>Aşağıdaki kişisel veri kategorileri işlenebilir:</p>
        <ul className="list-disc space-y-2 pl-5">
          <li><strong>Kimlik:</strong> ad, soyad</li>
          <li><strong>İletişim:</strong> telefon numarası, e-posta adresi, adres</li>
          <li><strong>İşlem güvenliği:</strong> IP adresi, log kayıtları, çerez verileri</li>
          <li><strong>Müşteri işlem:</strong> talep ve şikâyet bilgileri, hizmet geçmişi</li>
        </ul>
      </>
    ),
  },
  {
    title: '3. Kişisel Verilerin İşlenme Amaçları',
    content: (
      <>
        <ul className="list-disc space-y-2 pl-5">
          <li>Klima satış, montaj, bakım ve servis hizmetlerinin sunulması</li>
          <li>Müşteri ilişkileri yönetimi ve iletişim taleplerinin karşılanması</li>
          <li>Sözleşme süreçlerinin yürütülmesi ve faturalandırma</li>
          <li>Web sitesi güvenliği, analitik ve reklam performans ölçümü</li>
          <li>Yetkili kamu kurum ve kuruluşlarına bilgi verilmesi (yasal zorunluluk)</li>
        </ul>
      </>
    ),
  },
  {
    title: '4. Kişisel Verilerin Aktarılması',
    content: (
      <>
        <p>Kişisel verileriniz aşağıdaki alıcı gruplarına aktarılabilir:</p>
        <ul className="list-disc space-y-2 pl-5">
          <li>İş ortaklarımız ve tedarikçilerimiz (montaj, lojistik, teknik servis)</li>
          <li>Barındırma (hosting) ve bilişim altyapı hizmet sağlayıcıları</li>
          <li>Analitik ve reklam platformları (Google Ads vb.)</li>
          <li>Yetkili kamu kurum ve kuruluşları</li>
        </ul>
        <p>
          Yurt dışına aktarım söz konusu olduğunda KVKK&apos;nın 9. maddesine uygun hukuki
          sebepler ve gerekli güvenlik tedbirleri uygulanır.
        </p>
      </>
    ),
  },
  {
    title: '5. Kişisel Veri Toplamanın Yöntemi ve Hukuki Sebebi',
    content: (
      <>
        <p>
          Verileriniz web sitesi, telefon, e-posta, şubelerimiz ve yazılı formlar aracılığıyla
          otomatik veya otomatik olmayan yollarla toplanır.
        </p>
        <p>Hukuki sebepler:</p>
        <ul className="list-disc space-y-2 pl-5">
          <li>KVKK md. 5/2 (c): Sözleşmenin kurulması veya ifası</li>
          <li>KVKK md. 5/2 (ç): Veri sorumlusunun hukuki yükümlülüğü</li>
          <li>KVKK md. 5/2 (f): Meşru menfaat</li>
          <li>KVKK md. 5/1: Açık rıza (pazarlama iletişimi ve zorunlu olmayan çerezler için)</li>
        </ul>
      </>
    ),
  },
  {
    title: '6. İlgili Kişinin Hakları (KVKK md. 11)',
    content: (
      <>
        <p>KVKK kapsamında aşağıdaki haklara sahipsiniz:</p>
        <ul className="list-disc space-y-2 pl-5">
          <li>Kişisel verilerinizin işlenip işlenmediğini öğrenme</li>
          <li>İşlenmişse buna ilişkin bilgi talep etme</li>
          <li>İşlenme amacını ve amacına uygun kullanılıp kullanılmadığını öğrenme</li>
          <li>Yurt içinde veya yurt dışında aktarıldığı üçüncü kişileri bilme</li>
          <li>Eksik veya yanlış işlenmişse düzeltilmesini isteme</li>
          <li>KVKK md. 7 kapsamında silinmesini veya yok edilmesini isteme</li>
          <li>Otomatik sistemler ile analiz edilmesi suretiyle aleyhinize bir sonucun ortaya çıkmasına itiraz etme</li>
          <li>Kanuna aykırı işlenmesi sebebiyle zarara uğramanız hâlinde tazminat talep etme</li>
        </ul>
        <p>
          Başvurularınızı <a href="mailto:vedel@vedel.com.tr">vedel@vedel.com.tr</a> adresine
          iletebilirsiniz. Talepler en geç 30 gün içinde sonuçlandırılır.
        </p>
      </>
    ),
  },
]

export default function KvkkPage() {
  return (
    <LegalPageLayout
      title="KVKK Aydınlatma Metni"
      subtitle="6698 sayılı Kişisel Verilerin Korunması Kanunu kapsamında bilgilendirme metni."
      lastUpdated="6 Haziran 2026"
      sections={sections}
    />
  )
}
