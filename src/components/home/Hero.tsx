'use client'

import { useState } from 'react'
import Image from 'next/image'
import Link from 'next/link'
import { ArrowRight, Snowflake, Shield, Clock, Store, Wrench, Settings, RefreshCw, ChevronDown, FileText, Zap, Building2 } from 'lucide-react'

export default function Hero() {
  const [showWarrantyTooltip, setShowWarrantyTooltip] = useState(false)
  const [openFaq, setOpenFaq] = useState<number | null>(null)

  const faqs = [
    {
      question: "Klima ne sıklıkla bakımı yapılmalı?",
      answer: "Klimalarınızın verimli çalışması ve ömrünü uzatmak için yılda en az 2 kez (mevsim geçişlerinde) profesyonel bakım yaptırmanızı öneriyoruz. Yaz ve kış sezonlarından önce bakım, cihazınızın performansını artırır."
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
      <section className="relative min-h-[90vh] flex items-center justify-center overflow-hidden bg-gradient-to-br from-slate-900 via-blue-900 to-cyan-700 pt-20 lg:pt-24 pb-12 md:pb-16">
        <div className="absolute inset-0 z-0">
          <div className="absolute inset-0 z-10 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmZmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PHBhdGggZD0iMzYgMzR2LTRoLTR2NGg0em0wLTh2LTRoLTR2NGg0em0wLTh2LTRoLTR2NGg0em0wLThWMmgtNHY0aDR6TTYgMzR2LTRIMnY0aDR6bTAtOHYtNEgydjRoNHptMC04di00SDJ2NGg0em0wLThWMkgydjRoNHoiLz48L2c+PC9nPjwvc3ZnPg==')] opacity-10" />
          <Image
            src="/sakura.jpg"
            alt="Background"
            fill
            priority
            quality={90}
            className="object-cover object-center blur-sm brightness-50"
          />
        </div>

        <div className="absolute top-20 left-10 w-40 sm:w-72 h-40 sm:h-72 bg-cyan-500/20 rounded-full blur-3xl" />
        <div className="absolute bottom-20 right-10 w-48 sm:w-96 h-48 sm:h-96 bg-blue-500/20 rounded-full blur-3xl" />

        <div className="container mx-auto px-4 relative z-10">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-sm rounded-full mb-8">
              <Snowflake className="w-5 h-5 text-cyan-300" />
              <span className="text-cyan-100 text-sm font-medium">Profesyonel Klima Danışmanlığı</span>
            </div>

            <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold text-white mb-6 leading-tight">
              Size En Uygun{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400">
                Klimanızı Seçin
              </span>
            </h1>

            <p className="text-lg md:text-xl text-blue-100 mb-10 max-w-2xl mx-auto">
              Mitsubishi Heavy Industries ve Euroform yetkili bayisi olarak, iklimlendirme ihtiyaçlarınızda profesyonel rehberlik ve uçtan uca çözümler sunuyoruz. Uzman kadromuzla hızlı kurulum ve satış sonrası güvenilir servis ayrıcalığını yaşayın.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                href="/klimani-sec"
                className="group inline-flex items-center gap-3 px-8 py-4 bg-red-600 text-white font-bold text-lg rounded-xl hover:bg-red-700 transition-all duration-300 shadow-lg hover:shadow-xl hover:-translate-y-1"
              >
                Hemen Klimanı Seç
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>

              <a
                href="tel:+902244131617"
                className="inline-flex items-center gap-3 px-8 py-4 bg-white/10 backdrop-blur-sm text-white font-semibold text-lg rounded-xl hover:bg-white/20 transition-all duration-300"
              >
                <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                Hemen Arayın
              </a>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 sm:gap-6 mt-10 sm:mt-16 pt-6 sm:pt-8 border-t border-white/10">
              <div className="flex items-center justify-center gap-3 text-blue-100 relative">
                <Shield className="w-6 h-6 text-cyan-400" />
                <span
                  className="font-medium cursor-pointer hover:text-cyan-300 transition-colors"
                  onClick={() => setShowWarrantyTooltip(!showWarrantyTooltip)}
                  onMouseEnter={() => setShowWarrantyTooltip(true)}
                  onMouseLeave={() => setShowWarrantyTooltip(false)}
                >
                  5 - 2 Yıl Garanti *
                </span>

                {showWarrantyTooltip && (
                  <div className="absolute top-full mt-3 left-1/2 -translate-x-1/2 w-64 bg-white text-gray-800 text-sm rounded-lg shadow-xl p-4 z-20">
                    <div className="text-left space-y-2">
                      <p className="font-semibold text-gray-900 mb-2">Garanti Süreleri</p>
                      <div className="flex justify-between">
                        <span>MHI Klimalar:</span>
                        <span className="font-semibold text-green-600">5 Yıl</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Euroform Klimalar:</span>
                        <span className="font-semibold text-green-600">2 Yıl</span>
                      </div>
                    </div>
                    <div className="absolute -top-2 left-1/2 -translate-x-1/2 w-4 h-4 bg-white rotate-45" />
                  </div>
                )}
              </div>
              <div className="flex items-center justify-center gap-3 text-blue-100">
                <Snowflake className="w-6 h-6 text-cyan-400" />
                <span className="font-medium">Uzman Kadro</span>
              </div>
              <div className="flex items-center justify-center gap-3 text-blue-100">
                <Clock className="w-6 h-6 text-cyan-400" />
                <span className="font-medium">Hızlı Servis Çözümleri</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="bg-gradient-to-b from-blue-50 to-white py-20">
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
