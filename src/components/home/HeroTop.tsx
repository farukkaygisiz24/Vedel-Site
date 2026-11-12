'use client'

import { useState } from 'react'
import Link from 'next/link'
import { ArrowRight, Snowflake, Shield, Store, Wrench, Info } from 'lucide-react'
import { categories } from './heroData'
import HeroBackground from './HeroBackground'
import HeroBrandCards from './HeroBrandCards'
import { CAMPAIGN_SURFACE_CLASS } from '@/config/campaign'

const isCleanHero = (hideLeadContent: boolean, hideCategoryGrid: boolean) =>
  !hideLeadContent && hideCategoryGrid

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

  const cleanHero = isCleanHero(hideLeadContent, hideCategoryGrid)

  return (
    <section
      className={`relative flex overflow-hidden ${
        cleanHero
          ? 'min-h-[100svh] items-end bg-neutral-950 pb-10 pt-24 lg:items-center lg:pb-16'
          : hideLeadContent && hideCategoryGrid
            ? 'aspect-video w-full max-h-[calc(100vh-4rem)] bg-white pb-0 pt-16 lg:pt-8'
            : hideLeadContent
              ? 'min-h-[70vh] flex-col justify-end bg-white pb-8 pt-16 lg:pt-8'
              : 'min-h-[90vh] items-center bg-slate-900 pb-8 pt-16 lg:min-h-[85vh] lg:pt-8'
      }`}
    >
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
          <div className="absolute top-20 left-10 h-40 w-40 rounded-full bg-cyan-500/20 blur-3xl sm:h-72 sm:w-72" />
          <div className="absolute bottom-20 right-10 h-48 w-48 rounded-full bg-blue-500/20 blur-3xl sm:h-96 sm:w-96" />
        </>
      )}

      <div className="container relative z-10 mx-auto px-4 sm:px-6">
        {cleanHero && (
          <div className="mx-auto max-w-3xl animate-hero-rise text-center lg:mx-0 lg:max-w-xl lg:text-left">
            <p className="mb-4 text-sm font-semibold tracking-[0.28em] text-white/90 sm:text-base">
              VEDEL
            </p>

            <h1 className="mb-4 text-4xl font-bold leading-[1.05] tracking-tight text-white drop-shadow-[0_2px_20px_rgba(0,0,0,0.45)] sm:text-5xl lg:text-6xl">
              Bursa&apos;da Japon
              <span className="mt-1 block text-red-500">iklimlendirme.</span>
            </h1>

            <p className="mx-auto mb-8 max-w-lg text-base leading-relaxed text-white/75 sm:text-lg lg:mx-0">
              Mitsubishi Heavy Industries ve Euroform yetkili bayisi.
              5 yıl garanti, profesyonel montaj ve servis.
            </p>

            <div className="mb-8 flex flex-col items-stretch justify-center gap-3 sm:flex-row sm:items-center lg:justify-start">
              <Link
                href="/klimani-sec"
                className="group inline-flex items-center justify-center gap-2 rounded-md bg-red-600 px-7 py-3.5 text-base font-bold text-white transition-colors hover:bg-red-700"
              >
                Klimanı Seç
                <ArrowRight className="h-5 w-5 transition-transform group-hover:translate-x-0.5" />
              </Link>
              <a
                href="tel:+902244132316"
                className="inline-flex items-center justify-center gap-2 rounded-md border border-white/30 bg-white/5 px-7 py-3.5 text-base font-semibold text-white transition-colors hover:bg-white/10"
              >
                (0224) 413 23 16
              </a>
            </div>

            <div className="flex flex-wrap items-center justify-center gap-x-5 gap-y-2 text-sm text-white/60 lg:justify-start">
              <div
                className="relative"
                onMouseEnter={() => setWarrantyNoteOpen(true)}
                onMouseLeave={() => setWarrantyNoteOpen(false)}
              >
                <button
                  type="button"
                  aria-expanded={warrantyNoteOpen}
                  aria-describedby="warranty-note-clean"
                  onClick={() => setWarrantyNoteOpen((open) => !open)}
                  className="inline-flex items-center gap-1.5 transition-colors hover:text-white"
                >
                  <Shield className="h-4 w-4 shrink-0" />
                  <span>5 yıl garanti</span>
                  <Info className="h-3.5 w-3.5 shrink-0 opacity-70" />
                </button>

                <div
                  id="warranty-note-clean"
                  role="tooltip"
                  className={`absolute bottom-full left-1/2 z-50 mb-2 w-72 max-w-[calc(100vw-2rem)] -translate-x-1/2 rounded-lg border border-white/15 bg-neutral-950/95 p-3 shadow-xl transition-all duration-200 lg:left-0 lg:translate-x-0 ${
                    warrantyNoteOpen
                      ? 'pointer-events-auto translate-y-0 opacity-100 visible'
                      : 'pointer-events-none translate-y-1 opacity-0 invisible'
                  }`}
                >
                  <p className="text-left text-xs leading-relaxed text-white/80">
                    <span className="font-semibold text-white">Garanti:</span> MHI 5 yıl, Euroform 2 yıl.
                  </p>
                </div>
              </div>
              <span className="hidden text-white/25 sm:inline" aria-hidden>
                ·
              </span>
              <span className="inline-flex items-center gap-1.5">
                <Store className="h-4 w-4 shrink-0" />
                Yetkili bayi
              </span>
              <span className="hidden text-white/25 sm:inline" aria-hidden>
                ·
              </span>
              <span className="inline-flex items-center gap-1.5">
                <Wrench className="h-4 w-4 shrink-0" />
                Profesyonel montaj
              </span>
            </div>
          </div>
        )}

        {!hideLeadContent && !cleanHero && (
          <div className="grid items-center gap-8 lg:grid-cols-2 lg:gap-12">
            <div className="text-center lg:text-left">
              <div className="mb-6 inline-flex items-center gap-2 rounded-full bg-white/10 px-4 py-2 backdrop-blur-sm">
                <Snowflake className="h-5 w-5 text-cyan-300" />
                <span className="text-sm font-medium text-cyan-100">Mitsubishi Heavy & Euroform Yetkili Bayi</span>
              </div>

              <h1 className="mb-4 text-3xl font-bold leading-tight text-white sm:text-4xl lg:mb-6 lg:text-5xl xl:text-6xl">
                <span className="animate-gradient bg-gradient-to-r from-cyan-300 via-white to-cyan-300 bg-[length:200%_auto] bg-clip-text text-transparent">
                  Bursa&apos;nın İklimlendirme Uzmanından
                </span>
              </h1>
              <h2 className="mb-4 text-xl font-semibold text-cyan-300 sm:text-2xl lg:mb-6 lg:text-3xl">
                Japon Teknolojisiyle Tanışın
              </h2>

              <p className="mx-auto mb-6 max-w-xl text-base leading-relaxed text-blue-100 lg:mx-0 lg:mb-8 lg:text-lg">
                <span className="font-semibold text-white">Vedel Klima</span>&apos;nın 25 yıllık tecrübesiyle{' '}
                <span className="font-medium text-cyan-300">Mitsubishi Heavy Industries</span> ve{' '}
                <span className="font-medium text-cyan-300">Euroform</span> kalitesini buluşturuyoruz.
                <span className="font-medium text-white"> 5 yıl garanti</span> ve kusursuz servis güvencesiyle,
                yaşam alanınız için en doğru tercihi birlikte yapalım.
              </p>

              <div className="mb-6 flex flex-col items-center justify-center gap-3 sm:flex-row lg:mb-8 lg:justify-start lg:gap-4">
                <Link
                  href="/klimani-sec"
                  className="group inline-flex w-full items-center justify-center gap-3 rounded-xl bg-red-600 px-6 py-3 text-base font-bold text-white shadow-lg transition-all duration-300 hover:-translate-y-1 hover:bg-red-700 hover:shadow-xl sm:w-auto lg:px-8 lg:py-4 lg:text-lg"
                >
                  Klimanı Seç
                  <ArrowRight className="h-5 w-5 transition-transform group-hover:translate-x-1" />
                </Link>

                <a
                  href="tel:+902244132316"
                  className="inline-flex w-full items-center justify-center gap-3 rounded-xl bg-white/10 px-6 py-3 text-base font-semibold text-white backdrop-blur-sm transition-all duration-300 hover:bg-white/20 sm:w-auto lg:px-8 lg:py-4 lg:text-lg"
                >
                  <span className="h-2 w-2 animate-pulse rounded-full bg-green-400" />
                  Hemen Arayın
                </a>
              </div>

              <div className="flex flex-wrap items-center justify-center gap-4 text-sm lg:justify-start lg:gap-6">
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
                    className="flex cursor-help items-center gap-2 text-blue-100 transition-colors hover:text-white"
                  >
                    <Shield className="h-5 w-5 shrink-0 text-cyan-400" />
                    <span className="font-medium">5 Yıl Garanti</span>
                    <Info className="h-3.5 w-3.5 shrink-0 text-cyan-400/70" />
                  </button>

                  <div
                    id="warranty-note"
                    role="tooltip"
                    className={`absolute bottom-full left-1/2 z-50 mb-2 w-80 max-w-[calc(100vw-2rem)] -translate-x-1/2 rounded-xl border border-white/20 bg-slate-900/95 p-3.5 shadow-xl backdrop-blur-md transition-all duration-200 lg:left-0 lg:translate-x-0 ${
                      warrantyNoteOpen
                        ? 'pointer-events-auto translate-y-0 opacity-100 visible'
                        : 'pointer-events-none translate-y-1 opacity-0 invisible'
                    }`}
                  >
                    <div className="absolute -bottom-1.5 left-1/2 h-3 w-3 -translate-x-1/2 rotate-45 border-r border-b border-white/20 bg-slate-900/95 lg:left-6 lg:translate-x-0" />
                    <p className="text-xs leading-relaxed text-blue-100">
                      <span className="font-semibold text-white">Garanti koşulu:</span>{' '}
                      MHI 5 yıl, Euroform 2 yıl garanti. Trend (ZSP) serisi ile Profesyonel seriler istisnadır.
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2 text-blue-100">
                  <Store className="h-5 w-5 text-cyan-400" />
                  <span className="font-medium">Yetkili Bayi</span>
                </div>
                <div className="flex items-center gap-2 text-blue-100">
                  <Wrench className="h-5 w-5 text-cyan-400" />
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
            <div className="grid grid-cols-2 gap-3 md:grid-cols-4 md:gap-4">
              {categories.map((category, index) => (
                <Link
                  key={index}
                  href={category.href}
                  className="group rounded-xl bg-white/10 p-4 backdrop-blur-sm transition-all duration-300 hover:-translate-y-2 hover:bg-white/20 hover:shadow-xl hover:shadow-cyan-500/20 md:p-5"
                >
                  <div
                    className={`mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br ${category.color} transition-all duration-300 group-hover:scale-110 group-hover:rotate-3 md:h-12 md:w-12`}
                  >
                    <category.icon className="h-5 w-5 text-white md:h-6 md:w-6" />
                  </div>
                  <h3 className="mb-1 text-sm font-bold text-white transition-colors group-hover:text-cyan-300 md:text-base">
                    {category.name}
                  </h3>
                  <p className="text-xs text-blue-200 md:text-sm">{category.desc}</p>
                  <div className="mt-3 flex items-center gap-1 text-xs text-cyan-300 opacity-0 transition-opacity group-hover:opacity-100">
                    <span>Keşfet</span>
                    <ArrowRight className="h-3 w-3 transition-transform group-hover:translate-x-1" />
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
