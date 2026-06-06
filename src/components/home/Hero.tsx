'use client'

import { useState } from 'react'
import Link from 'next/link'
import { ArrowRight, Store, Wrench, Settings, RefreshCw, ChevronDown, FileText, Zap, Building2 } from 'lucide-react'
import { CAMPAIGN_HERO_ENABLED, CAMPAIGN_SURFACE_CLASS } from '@/config/campaign'
import HeroDefaultTop from './HeroDefaultTop'
import HeroCampaignTop from './HeroCampaignTop'

export default function Hero() {
  const [openFaq, setOpenFaq] = useState<number | null>(null)

  const faqs = [
    {
      question: "Klima ne sıklıkla bakımı yapılmalı?",
      answer: "Klimanızın verimli çalışması ve ömrünü uzatmak için yılda en az 2 kez (mevsim geçişlerinde) profesyonel bakım yaptırmanızı öneriyoruz. Yaz ve kış sezonlarından önce bakım, cihazlarınızın performansını artırır."
    },
    {
      question: "Inverter klima nedir, avantajları nelerdir?",
      answer: "Inverter klimalar, kompresör hızını ortam sıcaklığına göre ayarlayarak enerji tasarrufu sağlar. Geleneksel klimalara göre %30-50 daha az enerji tüketir, daha sessiz çalışır ve sıcaklık dalgalanmalarını önleyerek daha konforlu bir ortam sunar."
    },
    {
      question: "Klimanın BTU değeri nasıl hesaplanır?",
      answer: "BTU (British Thermal Unit), klimanın soğutma kapasitesini ifade eder. Odanızın metrekaresini 2.2 ile bölerek yaklaşık BTU ihtiyacınızı hesaplayabilirsiniz. Örneğin: 20 m² oda için yaklaşık 9.000 BTU kapasiteli klima yeterlidir."
    },
    {
      question: "Garanti kapsamına neler dahildir?",
      answer: "Garanti kapsamında üretim hatalarından kaynaklanan arızalar, kompresör ve elektronik kart arızaları yer alır. Garanti süresi MHI klimalarda 5 yıl, Euroform klimalarda 2 yıldır. Yanlış montaj, kullanım hatası ve düzenli bakımın yapılmaması garanti kapsamı dışındadır."
    },
    {
      question: "Klima montajı ne kadar sürer?",
      answer: "Standart bir split klima montajı, genellikle 1.5 - 2 saat arasında tamamlanır. Montaj süresi, mekanın durumuna, duvar tipine ve tesisat gereksinimlerine göre değişebilir. Multi sistem veya VRF kurulumları daha uzun sürebilir."
    }
  ]

  return (
    <>
      {CAMPAIGN_HERO_ENABLED ? <HeroCampaignTop /> : <HeroDefaultTop />}

      <section
        className={
          CAMPAIGN_HERO_ENABLED
            ? `${CAMPAIGN_SURFACE_CLASS} py-20 border-t border-[#e8e0d4]`
            : 'bg-gradient-to-b from-blue-50 to-white py-20'
        }
      >
        <div className="container mx-auto px-4 max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <span className="inline-block px-4 py-1.5 bg-blue-600 text-white text-xs font-bold tracking-wider rounded-full mb-4">
              NEDEN VEDEL?
            </span>
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Neden Biz?
            </h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              İklimlendirme sektöründeki köklü tecrübemizle, konforunuzu ve cihaz verimliliğinizi en üst seviyeye taşıyan profesyonel çözümler üretiyoruz.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-2xl hover:-translate-y-2 transition-all duration-300 relative overflow-hidden group">
              <div className="absolute top-0 left-0 w-full h-1 bg-blue-600"></div>
              <div className="w-14 h-14 bg-blue-50 rounded-2xl flex items-center justify-center mb-4">
                <Store className="w-7 h-7 text-blue-600" />
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">Yetkili Satış</h3>
              <p className="text-gray-600 text-sm mb-4">
                MHI ve Euroform markalarının yetkili satış noktasıyız. Orijinal ürünler ve garantili hizmet.
              </p>
              <Link href="/hakkimizda" className="inline-flex items-center text-blue-600 font-semibold text-sm hover:text-blue-800">
                Detaylı Bilgi <ArrowRight className="w-4 h-4 ml-1" />
              </Link>
            </div>

            <div className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-2xl hover:-translate-y-2 transition-all duration-300 relative overflow-hidden group">
              <div className="absolute top-0 left-0 w-full h-1 bg-blue-600"></div>
              <div className="w-14 h-14 bg-blue-50 rounded-2xl flex items-center justify-center mb-4">
                <Wrench className="w-7 h-7 text-blue-600" />
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">Yetkili Servis</h3>
              <p className="text-gray-600 text-sm mb-4">
                Tüm ürünlerimizde yetkili servis hizmeti. Garanti kapsamında profesyonel müdahale.
              </p>
              <Link href="/hakkimizda" className="inline-flex items-center text-blue-600 font-semibold text-sm hover:text-blue-800">
                Detaylı Bilgi <ArrowRight className="w-4 h-4 ml-1" />
              </Link>
            </div>

            <div className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-2xl hover:-translate-y-2 transition-all duration-300 relative overflow-hidden group">
              <div className="absolute top-0 left-0 w-full h-1 bg-blue-600"></div>
              <div className="w-14 h-14 bg-blue-50 rounded-2xl flex items-center justify-center mb-4">
                <Settings className="w-7 h-7 text-blue-600" />
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">Montaj & Kurulum</h3>
              <p className="text-gray-600 text-sm mb-4">
                Uzman ekibimizle güvenli ve profesyonel montaj. Doğru kurulum için detaylı çözümler.
              </p>
              <Link href="/hakkimizda" className="inline-flex items-center text-blue-600 font-semibold text-sm hover:text-blue-800">
                Detaylı Bilgi <ArrowRight className="w-4 h-4 ml-1" />
              </Link>
            </div>

            <div className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-2xl hover:-translate-y-2 transition-all duration-300 relative overflow-hidden group">
              <div className="absolute top-0 left-0 w-full h-1 bg-blue-600"></div>
              <div className="w-14 h-14 bg-blue-50 rounded-2xl flex items-center justify-center mb-4">
                <RefreshCw className="w-7 h-7 text-blue-600" />
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">Bakım & Onarım</h3>
              <p className="text-gray-600 text-sm mb-4">
                Periyodik bakım ve arıza çözümleri. Cihazlarınızı uzun ömürlü kullanmanız için hizmetinizdeyiz.
              </p>
              <Link href="/hakkimizda" className="inline-flex items-center text-blue-600 font-semibold text-sm hover:text-blue-800">
                Detaylı Bilgi <ArrowRight className="w-4 h-4 ml-1" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      <section className="bg-gradient-to-b from-green-50 to-white py-20">
        <div className="container mx-auto px-4 max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <span className="inline-block px-4 py-1.5 bg-green-600 text-white text-xs font-bold tracking-wider rounded-full mb-4">
              KLİMA SİSTEMLERİ
            </span>
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Ne Yapıyoruz?
            </h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              İhtiyacınıza uygun klimayı seçin. Konut, işyeri ve endüstriyel alanlar için çözümlerimiz.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <Link href="/urunler/splitsistemler" className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-2xl hover:-translate-y-2 transition-all duration-300 group">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4 group-hover:bg-green-600 transition-colors">
                <Building2 className="w-8 h-8 text-green-600 group-hover:text-white transition-colors" />
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">Split Sistemler</h3>
              <p className="text-gray-600 text-sm mb-4">
                Ev ve küçük ofisler için tek ünite ile mükemmel soğutma ve ısıtma çözümleri.
              </p>
              <span className="inline-flex items-center text-green-600 font-semibold text-sm group-hover:text-green-700">
                Detaylı Bilgi <ArrowRight className="w-4 h-4 ml-1" />
              </span>
            </Link>

            <Link href="/urunler/multisistemler" className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-2xl hover:-translate-y-2 transition-all duration-300 group">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4 group-hover:bg-green-600 transition-colors">
                <Settings className="w-8 h-8 text-green-600 group-hover:text-white transition-colors" />
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">Multi Sistemler</h3>
              <p className="text-gray-600 text-sm mb-4">
                Bir dış üniteye bağlanan birden fazla iç ünite ile esnek iklimlendirme.
              </p>
              <span className="inline-flex items-center text-green-600 font-semibold text-sm group-hover:text-green-700">
                Detaylı Bilgi <ArrowRight className="w-4 h-4 ml-1" />
              </span>
            </Link>

            <Link href="/urunler/profesyonelsistemler" className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-2xl hover:-translate-y-2 transition-all duration-300 group">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4 group-hover:bg-green-600 transition-colors">
                <Store className="w-8 h-8 text-green-600 group-hover:text-white transition-colors" />
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">Profesyonel Sistemler</h3>
              <p className="text-gray-600 text-sm mb-4">
                Ticari ve endüstriyel alanlar için yüksek kapasiteli profesyonel çözümler.
              </p>
              <span className="inline-flex items-center text-green-600 font-semibold text-sm group-hover:text-green-700">
                Detaylı Bilgi <ArrowRight className="w-4 h-4 ml-1" />
              </span>
            </Link>

            <Link href="/urunler/vrfsistemler" className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-2xl hover:-translate-y-2 transition-all duration-300 group">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4 group-hover:bg-green-600 transition-colors">
                <Building2 className="w-8 h-8 text-green-600 group-hover:text-white transition-colors" />
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">VRF Sistemler</h3>
              <p className="text-gray-600 text-sm mb-4">
                Büyük binalar ve komple tesisler için merkezi yönetimli ileri teknoloji sistemler.
              </p>
              <span className="inline-flex items-center text-green-600 font-semibold text-sm group-hover:text-green-700">
                Detaylı Bilgi <ArrowRight className="w-4 h-4 ml-1" />
              </span>
            </Link>
          </div>
        </div>
      </section>

      <section className="bg-gradient-to-b from-orange-50 to-white py-20">
        <div className="container mx-auto px-4 max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <span className="inline-block px-4 py-1.5 bg-orange-500 text-white text-xs font-bold tracking-wider rounded-full mb-4">
              BİLGİ MERKEZİ
            </span>
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Klima Hakkında
            </h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Klimanızdan maksimum verimi almak için bilmeniz gereken önemli konular
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-2xl hover:-translate-y-2 transition-all duration-300">
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mb-4">
                <Wrench className="w-6 h-6 text-orange-500" />
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-3">
                Klima Bakımı Ne Zaman Yapılmalı?
              </h3>
              <p className="text-gray-600 text-sm leading-relaxed mb-4">
                Klimanızın verimli çalışması ve ömrünü uzatmak için yılda en az 2 kez, mevsim geçişlerinde profesyonel bakım yaptırmanızı öneriyoruz.
              </p>
            </div>

            <div className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-2xl hover:-translate-y-2 transition-all duration-300">
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mb-4">
                <Zap className="w-6 h-6 text-orange-500" />
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-3">
                Inverter Klima ile Enerji Tasarrufu
              </h3>
              <p className="text-gray-600 text-sm leading-relaxed mb-4">
                Inverter klimalar, kompresör hızını ayarlayarak %30-50 arasında enerji tasarrufu sağlar. Daha sessiz çalışır ve konforlu bir ortam sunar.
              </p>
            </div>

            <div className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-2xl hover:-translate-y-2 transition-all duration-300">
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mb-4">
                <FileText className="w-6 h-6 text-orange-500" />
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-3">
                Montajda Dikkat Edilmesi Gereken 5 Kritik Nokta
              </h3>
              <p className="text-gray-600 text-sm leading-relaxed mb-4">
                Doğru konum seçimi, drenaj sistemi, gaz kaçağı kontrolü, elektrik tesisatı ve profesyonel montaj ekibi. Bu 5 maddeye dikkat edin.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="bg-gradient-to-b from-purple-50 to-white py-20">
        <div className="container mx-auto px-4 max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <span className="inline-block px-4 py-1.5 bg-purple-600 text-white text-xs font-bold tracking-wider rounded-full mb-4">
              SSS
            </span>
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Sıkça Sorulan Sorular
            </h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Müşterilerimizden en çok gelen sorular ve cevapları
            </p>
          </div>

          <div className="max-w-3xl mx-auto space-y-4">
            {faqs.map((faq, index) => (
              <div
                key={index}
                className="border border-purple-200 rounded-xl overflow-hidden bg-white shadow-sm hover:shadow-md transition-shadow"
              >
                <button
                  onClick={() => setOpenFaq(openFaq === index ? null : index)}
                  className="w-full flex items-center justify-between p-5 text-left bg-purple-50 hover:bg-purple-100 transition-colors"
                >
                  <span className="font-semibold text-gray-900 pr-4">
                    {faq.question}
                  </span>
                  <ChevronDown
                    className={`w-5 h-5 text-purple-500 flex-shrink-0 transition-transform duration-300 ${openFaq === index ? 'rotate-180' : ''}`}
                  />
                </button>
                <div
                  className={`overflow-hidden transition-all duration-300 ${openFaq === index ? 'max-h-96' : 'max-h-0'}`}
                >
                  <div className="p-5 text-gray-600 text-sm leading-relaxed border-t border-purple-100">
                    {faq.answer}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </>
  )
}
