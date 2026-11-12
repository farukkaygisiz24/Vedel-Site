'use client'

import { useState } from 'react'
import Link from 'next/link'
import { ArrowRight, ChevronDown } from 'lucide-react'
import {
  CAMPAIGN_CONTENT_BORDER_CLASS,
  CAMPAIGN_CONTENT_SURFACE_CLASS,
  CAMPAIGN_HERO_ENABLED,
} from '@/config/campaign'
import HeroDefaultTop from './HeroDefaultTop'
import HeroCampaignTop from './HeroCampaignTop'

export default function Hero() {
  const [openFaq, setOpenFaq] = useState<number | null>(null)

  const faqs = [
    {
      question: 'Klima montajı ne kadar sürer?',
      answer:
        'Standart bir split klima montajı, tesisat uygunsa genellikle 1,5-3 saat içinde tamamlanır. Duvar tipi, drenaj ve elektrik altyapısı işi uzatabilir. Multi ve VRF kurulumları keşif ve proje kapsamına göre daha uzun sürer.',
    },
    {
      question: 'Garanti kapsamına neler dahildir?',
      answer:
        'Üretim kaynaklı arızalar, kompresör ve elektronik kart sorunları garanti kapsamında değerlendirilir. MHI ürünlerde garanti süresi 5 yıl, Euroform ürünlerde 2 yıldır. Yetkisiz montaj, kullanım hatası ve düzenli bakımın ihmal edilmesi kapsam dışındadır.',
    },
    {
      question: 'Klimam yeterince soğutmuyor, neden olabilir?',
      answer:
        'Kirli filtre, dış ünite etrafında engel, yanlış kapasite seçimi veya gaz kaçağı sık görülen nedenlerdir. Önce filtreleri temizleyin; sorun sürerse yetkili servis ile kontrol ettirmenizi öneririz. Yaz öncesi bakım bu tür şikayetleri büyük ölçüde azaltır.',
    },
    {
      question: 'Split mi multi mi tercih etmeliyim?',
      answer:
        'Tek oda veya bağımsız kullanım için split yeterlidir. Birden fazla odayı tek dış üniteyle yönetmek, dış cepheyi sade tutmak veya yer tasarrufu istiyorsanız multi daha uygundur. Mekân planınıza göre Kayapa veya Özlüce şubelerimizde birlikte netleştiriyoruz.',
    },
    {
      question: 'Montajı neden yetkili servis yapmalı?',
      answer:
        'Markaya özel ölçüm, vakumlama ve devreye alma adımları doğru uygulanmazsa hem performans hem garanti süreci risk altına girer. Yetkili servis montajı, resmi garanti koşullarının geçerli kalması için kritiktir.',
    },
  ]

  return (
    <>
      {CAMPAIGN_HERO_ENABLED ? <HeroCampaignTop /> : <HeroDefaultTop />}

      <section
        className={
          CAMPAIGN_HERO_ENABLED
            ? `${CAMPAIGN_CONTENT_SURFACE_CLASS} border-t ${CAMPAIGN_CONTENT_BORDER_CLASS} py-16 sm:py-20`
            : 'border-t border-neutral-200/80 bg-white py-16 sm:py-20'
        }
      >
        <div className="mx-auto grid max-w-7xl gap-12 px-4 sm:px-6 lg:grid-cols-[minmax(0,1.05fr)_minmax(0,0.95fr)] lg:gap-16 lg:px-8">
          <div className="text-center lg:text-left">
            <p className="mb-3 text-sm font-semibold tracking-[0.2em] text-red-600">NEDEN VEDEL</p>
            <h2 className="mb-6 text-3xl font-bold tracking-tight text-neutral-900 sm:text-4xl lg:text-[2.65rem] lg:leading-[1.15]">
              Satıştan servise tek adres.
            </h2>
            <div className="mx-auto max-w-xl space-y-4 text-left text-[15px] leading-[1.75] text-neutral-600 sm:text-base lg:mx-0 lg:max-w-none">
              <p>
                Vedel Klima, Bursa&apos;da 25 yılı aşkın süredir iklimlendirme
                sektörünün içinde. Konuttan ofise, işletmeden üretim tesisine kadar
                aynı prensiple çalışıyoruz: doğru ürünü seçmek, doğru kurmak ve uzun
                yıllar sorunsuz çalışmasını sağlamak.
              </p>
              <p>
                Mitsubishi Heavy Industries ve Euroform yetkili bayisi olarak orijinal
                ürün gamını resmi garanti koşullarıyla sunuyoruz. Split ve multi
                sistemlerden profesyonel ve VRF çözümlerine kadar ihtiyaca göre
                yönlendiriyor; kapasite, enerji sınıfı ve mekân koşullarını birlikte
                değerlendirerek en doğru çözümü belirliyoruz.
              </p>
              <p>
                Satış sonrası süreçte de yanınızdayız. Montaj, periyodik bakım ve
                arıza müdahalesini aynı teknik ekiple yürütüyor; Kayapa ve Özlüce
                şubelerimizle Bursa genelinde kesintisiz destek sağlıyoruz.
              </p>
            </div>
            <Link
              href="/hakkimizda"
              className="group mx-auto mt-7 flex max-w-xl items-center justify-between gap-4 border-t border-neutral-200 pt-5 text-left transition-colors hover:border-red-600 lg:mx-0 lg:max-w-none"
            >
              <span className="min-w-0">
                <span className="block text-sm font-bold text-neutral-900 transition-colors group-hover:text-red-600">
                  Hakkımızda
                </span>
                <span className="mt-0.5 block text-xs text-neutral-500 sm:text-sm">
                  25 yıllık hikâyemizi tanıyın
                </span>
              </span>
              <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full border border-neutral-200 text-neutral-700 transition-colors group-hover:border-red-600 group-hover:bg-red-600 group-hover:text-white">
                <ArrowRight className="h-4 w-4" />
              </span>
            </Link>
          </div>

          <ul className="divide-y divide-neutral-200 border-y border-neutral-200">
            {[
              {
                title: 'Yetkili satış',
                text: 'MHI ve Euroform orijinal ürünleri, resmi dağıtım ve garanti güvencesiyle. İhtiyaca göre doğru kapasite ve seri seçiminde danışmanlık.',
              },
              {
                title: 'Yetkili servis',
                text: 'Garanti kapsamında uzman müdahale. Arıza anında muhatap bellidir; süreç yetkili servis standartlarıyla yönetilir.',
              },
              {
                title: 'Montaj & kurulum',
                text: 'Konum, tesisat ve drenaj doğru planlanmadan verimli sistem olmaz. Kurulumdan devreye almaya kadar aynı ekip sorumludur.',
              },
              {
                title: 'Bakım & onarım',
                text: 'Mevsim geçişlerinde periyodik bakım ve hızlı arıza çözümüyle cihaz ömrünü uzatır, enerji kaybını azaltırız.',
              },
            ].map((item, index) => (
              <li
                key={item.title}
                className="grid grid-cols-[auto_minmax(0,1fr)] gap-4 py-5 sm:gap-5 sm:py-6"
              >
                <span className="pt-0.5 font-display text-2xl leading-none text-red-600 sm:text-3xl">
                  {String(index + 1).padStart(2, '0')}
                </span>
                <div>
                  <h3 className="mb-1.5 text-base font-bold text-neutral-900 sm:text-lg">{item.title}</h3>
                  <p className="text-sm leading-relaxed text-neutral-600 sm:text-[15px] sm:leading-relaxed">{item.text}</p>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section
        className={
          CAMPAIGN_HERO_ENABLED
            ? `${CAMPAIGN_CONTENT_SURFACE_CLASS} border-t ${CAMPAIGN_CONTENT_BORDER_CLASS} py-16 sm:py-20`
            : 'border-t border-neutral-200/80 bg-[#f5f4f1] py-16 sm:py-20'
        }
      >
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mx-auto mb-8 max-w-2xl text-center lg:mb-10">
            <p className="mb-3 text-sm font-semibold tracking-[0.2em] text-red-600">
              KLİMA SİSTEMLERİ
            </p>
            <h2 className="mb-4 text-3xl font-bold tracking-tight text-neutral-900 sm:text-4xl">
              Ne yapıyoruz?
            </h2>
            <p className="text-base leading-relaxed text-neutral-600">
              Konuttan ticari alana, tek odadan büyük tesislere kadar MHI ve Euroform
              ürün gamıyla ihtiyaca uygun iklimlendirme çözümleri sunuyoruz. Satışın
              yanında montaj, bakım ve yetkili servis de aynı çatı altında; doğru
              sistemi seçmenizden devreye almaya kadar yanınızdayız.
            </p>
          </div>

          <div className="grid grid-cols-1 gap-px overflow-hidden rounded-sm bg-neutral-300/70 sm:grid-cols-2">
            {[
              {
                href: '/urunler/splitsistemler',
                tag: 'Konut & ofis',
                title: 'Split',
                text: "Ev ve küçük ofisler için tek iç üniteyle soğutma ve ısıtma. Trend'den Diamond'a kadar ekonomik giriş ve üst seri seçenekleriyle mekânınıza uygun kapasiteyi birlikte belirliyoruz.",
              },
              {
                href: '/urunler/multisistemler',
                tag: 'Çoklu oda',
                title: 'Multi',
                text: 'Bir dış üniteye birden fazla iç ünite bağlanır. Farklı odaları bağımsız sıcaklıkla yönetmek isteyen ev ve ofisler için esnek, yer tasarruflu bir çözüm sunar.',
              },
              {
                href: '/urunler/profesyonelsistemler',
                tag: 'Ticari alan',
                title: 'Profesyonel',
                text: 'Mağaza, restoran, ofis ve benzeri ticari alanlar için yüksek kapasiteli sistemler. Yoğun kullanımda kesintisiz performans ve enerji verimliliği odaklı seçim.',
              },
              {
                href: '/urunler/vrfsistemler',
                tag: 'Büyük tesis',
                title: 'VRF',
                text: 'Büyük binalar ve komple tesisler için merkezi yönetimli ileri teknoloji. Bölgesel kontrol, düşük işletme maliyeti ve ölçeklenebilir kapasite ile planlanır.',
              },
            ].map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="group flex flex-col bg-[#f5f4f1] p-5 transition-colors hover:bg-white sm:p-6"
              >
                <p className="mb-2 text-[11px] font-semibold tracking-[0.18em] text-red-600 uppercase">
                  {item.tag}
                </p>
                <h3 className="font-display mb-2 text-2xl tracking-tight text-neutral-900 sm:text-3xl">
                  {item.title}
                </h3>
                <p className="mb-4 flex-1 text-sm leading-relaxed text-neutral-600">
                  {item.text}
                </p>
                <span className="inline-flex items-center gap-2 text-sm font-bold text-neutral-900 transition-colors group-hover:text-red-600">
                  İncele
                  <ArrowRight className="h-4 w-4" />
                </span>
              </Link>
            ))}
          </div>
        </div>
      </section>

      <section className="border-t border-neutral-200/80 bg-white py-16 sm:py-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mb-10 max-w-2xl lg:mb-12">
            <p className="mb-3 text-sm font-semibold tracking-[0.2em] text-red-600">
              BİLGİ MERKEZİ
            </p>
            <h2 className="mb-4 text-3xl font-bold tracking-tight text-neutral-900 sm:text-4xl">
              Klima hakkında bilmeniz gerekenler
            </h2>
            <p className="text-base leading-relaxed text-neutral-600">
              Klima alırken ve kullanırken en çok merak edilen konular: doğru BTU
              kapasitesi, inverter teknolojisi ve periyodik bakım. Kısa rehberimizle
              bilinçli seçim yapmanıza yardımcı oluyoruz.
            </p>
          </div>

          <div className="grid grid-cols-1 gap-10 md:grid-cols-3 md:gap-8 lg:gap-12">
            {[
              {
                tag: 'Kapasite',
                title: 'Klima BTU nedir, nasıl hesaplanır?',
                text: 'BTU, klimanın soğutma ve ısıtma kapasitesini ifade eder. Yaklaşık hesap için oda metrekaresini 2,2 ile bölebilirsiniz; örneğin 20 m² için yaklaşık 9.000 BTU yeterlidir. Güneş alan cephe, tavan yüksekliği, yalıtım ve kişi sayısı da sonucu değiştirir. Düşük kapasite cihazı sürekli çalıştırır; fazla kapasite ise sık aç-kapa yapıp konforu bozar. Doğru seçim için yerinde keşif önerilir.',
              },
              {
                tag: 'Teknoloji',
                title: 'Inverter klima nedir, avantajları nelerdir?',
                text: 'Inverter klima, kompresör hızını ortam yüküne göre ayarlayan sistemdir. Sabit hızlı modellere göre yaklaşık %30-50 daha az enerji tüketebilir; sıcaklığı daha sabit tutar ve daha sessiz çalışır. Alırken SEER ve SCOP değerlerine, enerji sınıfına ve mekânınıza uygun kapasiteye bakmak önemlidir.',
              },
              {
                tag: 'Bakım',
                title: 'Klima bakımı ne sıklıkla yapılmalı?',
                text: 'Ev tipi klimalarda yılda en az bir, tercihen yaz ve kış sezonu öncesi iki kez profesyonel bakım önerilir. Yoğun kullanılan iş yerlerinde süre kısalabilir. Filtreleri kullanıcı düzenli temizleyebilir; eşanjör temizliği ve genel kontrol ise yetkili servisle yapılmalıdır. Düzenli bakım enerji tüketimini düşürür, kokuyu önler ve arıza riskini azaltır.',
              },
            ].map((item) => (
              <article
                key={item.title}
                className="border-t-2 border-neutral-900 pt-5 transition-colors hover:border-red-600"
              >
                <p className="mb-2 text-xs font-semibold tracking-[0.18em] text-red-600 uppercase">
                  {item.tag}
                </p>
                <h3 className="mb-3 text-lg font-bold text-neutral-900 sm:text-xl">
                  {item.title}
                </h3>
                <p className="text-sm leading-relaxed text-neutral-600 sm:text-[15px]">
                  {item.text}
                </p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="border-t border-neutral-200/80 bg-[#f5f4f1] py-16 sm:py-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mx-auto mb-10 max-w-2xl text-center lg:mb-12">
            <p className="mb-3 text-sm font-semibold tracking-[0.2em] text-red-600">SSS</p>
            <h2 className="mb-4 text-3xl font-bold tracking-tight text-neutral-900 sm:text-4xl">
              Sıkça sorulan sorular
            </h2>
            <p className="text-base leading-relaxed text-neutral-600">
              Montaj, garanti ve sistem seçimi hakkında en çok gelen sorular.
            </p>
          </div>

          <div className="mx-auto max-w-3xl border-y border-neutral-300/80">
            {faqs.map((faq, index) => {
              const isOpen = openFaq === index
              return (
                <div
                  key={faq.question}
                  className="border-b border-neutral-300/80 last:border-b-0"
                >
                  <button
                    type="button"
                    onClick={() => setOpenFaq(isOpen ? null : index)}
                    aria-expanded={isOpen}
                    aria-controls={`faq-answer-${index}`}
                    className="flex w-full items-center justify-between gap-4 py-5 text-left sm:py-6"
                  >
                    <span className="pr-2 text-sm font-semibold text-neutral-900 sm:text-base">
                      {faq.question}
                    </span>
                    <ChevronDown
                      aria-hidden="true"
                      className={`h-5 w-5 shrink-0 text-red-600 transition-transform duration-300 ${
                        isOpen ? 'rotate-180' : ''
                      }`}
                    />
                  </button>
                  <div
                    id={`faq-answer-${index}`}
                    role="region"
                    className={`overflow-hidden transition-all duration-300 ${
                      isOpen ? 'max-h-96' : 'max-h-0'
                    }`}
                  >
                    <p className="pb-5 text-sm leading-relaxed text-neutral-600 sm:pb-6 sm:text-[15px]">
                      {faq.answer}
                    </p>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </section>
    </>
  )
}
