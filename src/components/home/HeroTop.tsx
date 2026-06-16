'use client'

import { useState } from 'react'
import Link from 'next/link'
import { ArrowRight, Snowflake, Shield, Store, Wrench, Info } from 'lucide-react'
import { categories } from './heroData'
import HeroBackground from './HeroBackground'
import HeroBrandCards from './HeroBrandCards'
import { CAMPAIGN_SURFACE_CLASS } from '@/config/campaign'

type HeroTopProps = {
  backgroundSrc: string
  backgroundAlt: string
  backgroundVideoSrc?: string
  backgroundPosterSrc?: string
  backgroundClassName?: string
  backgroundVideoClassName?: string
  backgroundFitContain?: boolean
  backgroundContentInsetClassName?: string
  overlayClassName?: string
  showPattern?: boolean
  showDecorativeBlobs?: boolean
  hideLeadContent?: boolean
  hideCategoryGrid?: boolean
}

export default function HeroTop({
  backgroundSrc,
  backgroundAlt,
  backgroundVideoSrc,
  backgroundPosterSrc,
  backgroundClassName = 'object-cover object-center blur-sm brightness-50',
  backgroundVideoClassName,
  backgroundFitContain = false,
  backgroundContentInsetClassName,
  overlayClassName = 'bg-gradient-to-br from-slate-900/70 via-blue-900/50 to-cyan-900/30',
  showPattern = true,
  showDecorativeBlobs = true,
  hideLeadContent = false,
  hideCategoryGrid = false,
}: HeroTopProps) {
  const [warrantyNoteOpen, setWarrantyNoteOpen] = useState(false)
  const isCampaignVideoLayout = hideLeadContent && hideCategoryGrid && backgroundFitContain
  const contentInset = backgroundContentInsetClassName ?? 'px-4 sm:px-6 md:px-8 lg:px-12'

  if (isCampaignVideoLayout) {
    const campaignSpacing = 'gap-4 sm:gap-5 md:gap-6 lg:gap-8'
    const campaignInsetSpacing = 'pt-4 sm:pt-5 md:pt-6 lg:pt-8'

    return (
      <section className={`relative pb-6 sm:pb-7 lg:pb-8 ${CAMPAIGN_SURFACE_CLASS}`}>
        <div className={`${contentInset} ${campaignInsetSpacing}`}>
          <div className={`mx-auto flex max-w-7xl flex-col ${campaignSpacing}`}>
            <div className={`group relative aspect-video w-full overflow-hidden rounded-2xl border border-gray-200/90 shadow-sm transition-all duration-300 hover:-translate-y-0.5 hover:border-gray-300 hover:shadow-lg ${CAMPAIGN_SURFACE_CLASS}`}>
              <HeroBackground
                imageSrc={backgroundSrc}
                imageAlt={backgroundAlt}
                imageClassName={backgroundClassName}
                videoClassName={backgroundVideoClassName}
                videoSrc={backgroundVideoSrc}
                posterSrc={backgroundPosterSrc}
                overlayClassName={overlayClassName}
                showPattern={showPattern}
                aspectBoxLayout
              />
            </div>

            <HeroBrandCards
              variant="light"
              className="grid gap-4 sm:gap-5 lg:grid-cols-2 lg:gap-5"
            />
          </div>
        </div>
      </section>
    )
  }

  return (
    <section className={`relative flex overflow-hidden pt-16 lg:pt-8 pb-8 ${
      hideLeadContent && hideCategoryGrid
        ? 'aspect-video w-full max-h-[calc(100vh-4rem)] bg-white pb-0'
        : hideLeadContent
          ? 'min-h-[70vh] flex-col justify-end bg-white'
          : 'min-h-[90vh] lg:min-h-[85vh] items-center bg-slate-900'
    }`}>
      <div className="absolute inset-0 z-0">
        <HeroBackground
          imageSrc={backgroundSrc}
          imageAlt={backgroundAlt}
          imageClassName={backgroundClassName}
          videoClassName={backgroundVideoClassName}
          videoSrc={backgroundVideoSrc}
          posterSrc={backgroundPosterSrc}
          overlayClassName={overlayClassName}
          showPattern={showPattern}
          fitContain={backgroundFitContain}
          contentInsetClassName={backgroundContentInsetClassName}
        />
      </div>

      {showDecorativeBlobs && (
        <>
          <div className="absolute top-20 left-10 w-40 sm:w-72 h-40 sm:h-72 bg-cyan-500/20 rounded-full blur-3xl" />
          <div className="absolute bottom-20 right-10 w-48 sm:w-96 h-48 sm:h-96 bg-blue-500/20 rounded-full blur-3xl" />
        </>
      )}

      <div className="container mx-auto px-4 relative z-10">
        {!hideLeadContent && (
        <div className="grid lg:grid-cols-2 gap-8 lg:gap-12 items-center">
          <div className="text-center lg:text-left">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-sm rounded-full mb-6">
              <Snowflake className="w-5 h-5 text-cyan-300" />
              <span className="text-cyan-100 text-sm font-medium">Mitsubishi Heavy & Euroform Yetkili Bayi</span>
            </div>

            <h1 className="text-3xl sm:text-4xl lg:text-5xl xl:text-6xl font-bold text-white mb-4 lg:mb-6 leading-tight">
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 via-white to-cyan-300 bg-[length:200%_auto] animate-gradient">
                Bursa&apos;nın İklimlendirme Uzmanından
              </span>
            </h1>
            <h2 className="text-xl sm:text-2xl lg:text-3xl font-semibold text-cyan-300 mb-4 lg:mb-6">
              Japon Teknolojisiyle Tanışın
            </h2>

            <p className="text-base lg:text-lg text-blue-100 mb-6 lg:mb-8 max-w-xl mx-auto lg:mx-0 leading-relaxed">
              <span className="font-semibold text-white">Vedel Klima</span>&apos;nın 25 yıllık tecrübesiyle{' '}
              <span className="text-cyan-300 font-medium">Mitsubishi Heavy Industries</span> ve{' '}
              <span className="text-cyan-300 font-medium">Euroform</span> kalitesini buluşturuyoruz.
              <span className="text-white font-medium"> 8 yıl garanti</span> ve kusursuz servis güvencesiyle,
              yaşam alanınız için en doğru tercihi birlikte yapalım.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-3 lg:gap-4 mb-6 lg:mb-8">
              <Link
                href="/klimani-sec"
                className="group inline-flex items-center gap-3 px-6 lg:px-8 py-3 lg:py-4 bg-red-600 text-white font-bold text-base lg:text-lg rounded-xl hover:bg-red-700 transition-all duration-300 shadow-lg hover:shadow-xl hover:-translate-y-1 w-full sm:w-auto justify-center"
              >
                Klimanı Seç
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>

              <a
                href="tel:+902244132316"
                className="inline-flex items-center justify-center gap-3 px-6 lg:px-8 py-3 lg:py-4 bg-white/10 backdrop-blur-sm text-white font-semibold text-base lg:text-lg rounded-xl hover:bg-white/20 transition-all duration-300 w-full sm:w-auto"
              >
                <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                Hemen Arayın
              </a>
            </div>

            <div className="flex flex-wrap items-center justify-center lg:justify-start gap-4 lg:gap-6 text-sm">
              <div
                className="relative"
                onMouseEnter={() => setWarrantyNoteOpen(true)}
                onMouseLeave={() => setWarrantyNoteOpen(false)}
              >
                <button
                  type="button"
                  aria-expanded={warrantyNoteOpen}
                  aria-describedby="warranty-note"
                  onClick={() => setWarrantyNoteOpen((open) => !open)}
                  className="flex items-center gap-2 text-blue-100 hover:text-white transition-colors cursor-help"
                >
                  <Shield className="w-5 h-5 text-cyan-400 shrink-0" />
                  <span className="font-medium">8 Yıl Garanti</span>
                  <Info className="w-3.5 h-3.5 text-cyan-400/70 shrink-0" />
                </button>

                <div
                  id="warranty-note"
                  role="tooltip"
                  className={`absolute bottom-full left-1/2 lg:left-0 z-50 mb-2 w-80 max-w-[calc(100vw-2rem)] -translate-x-1/2 lg:translate-x-0 rounded-xl border border-white/20 bg-slate-900/95 p-3.5 shadow-xl backdrop-blur-md transition-all duration-200 ${
                    warrantyNoteOpen
                      ? 'pointer-events-auto translate-y-0 opacity-100 visible'
                      : 'pointer-events-none translate-y-1 opacity-0 invisible'
                  }`}
                >
                  <div className="absolute -bottom-1.5 left-1/2 lg:left-6 h-3 w-3 -translate-x-1/2 lg:translate-x-0 rotate-45 border-r border-b border-white/20 bg-slate-900/95" />
                  <p className="text-xs leading-relaxed text-blue-100">
                    <span className="font-semibold text-white">Garanti koşulu:</span>{' '}
                    MHI marka klimalarda 8 yıl garanti uygulanır. Trend (ZSP) serisi ile Profesyonel seriler istisnadır.
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2 text-blue-100">
                <Store className="w-5 h-5 text-cyan-400" />
                <span className="font-medium">Yetkili Bayi</span>
              </div>
              <div className="flex items-center gap-2 text-blue-100">
                <Wrench className="w-5 h-5 text-cyan-400" />
                <span className="font-medium">Profesyonel Montaj</span>
              </div>
            </div>
          </div>

          <div className="hidden lg:block">
            <HeroBrandCards className="relative space-y-4" />
          </div>
        </div>
        )}

        {!hideCategoryGrid && (
        <div className={hideLeadContent ? 'mt-auto' : 'mt-8 lg:mt-12'}>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4">
            {categories.map((category, index) => (
              <Link
                key={index}
                href={category.href}
                className="group bg-white/10 backdrop-blur-sm rounded-xl p-4 md:p-5 hover:bg-white/20 transition-all duration-300 hover:-translate-y-2 hover:shadow-xl hover:shadow-cyan-500/20"
              >
                <div className={`w-10 h-10 md:w-12 md:h-12 rounded-xl bg-gradient-to-br ${category.color} flex items-center justify-center mb-3 group-hover:scale-110 group-hover:rotate-3 transition-all duration-300`}>
                  <category.icon className="w-5 h-5 md:w-6 md:h-6 text-white" />
                </div>
                <h3 className="text-white font-bold text-sm md:text-base mb-1 group-hover:text-cyan-300 transition-colors">{category.name}</h3>
                <p className="text-blue-200 text-xs md:text-sm">{category.desc}</p>
                <div className="mt-3 flex items-center gap-1 text-cyan-300 text-xs opacity-0 group-hover:opacity-100 transition-opacity">
                  <span>Keşfet</span>
                  <ArrowRight className="w-3 h-3 group-hover:translate-x-1 transition-transform" />
                </div>
              </Link>
            ))}
          </div>
        </div>
        )}
      </div>
    </section>
  )
}
