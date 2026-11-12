'use client'

import { useCallback, useEffect, useLayoutEffect, useRef, useState } from 'react'
import Image from 'next/image'
import Link from 'next/link'
import { ArrowRight, ChevronLeft, ChevronRight } from 'lucide-react'
import { heroCatalogSeries } from './heroData'

const AUTOPLAY_MS = 5000
const PILL_MS = 320

type PillBox = { left: number; width: number }

export default function HeroCatalog() {
  const [active, setActive] = useState(0)
  const [paused, setPaused] = useState(false)
  const [progress, setProgress] = useState(0)
  const [pill, setPill] = useState<PillBox>({ left: 0, width: 0 })
  const [pillReady, setPillReady] = useState(false)
  const [pillMotion, setPillMotion] = useState(true)
  const progressRef = useRef(0)
  const listRef = useRef<HTMLDivElement>(null)
  const tabRefs = useRef<(HTMLButtonElement | null)[]>([])
  const activeRef = useRef(active)
  const count = heroCatalogSeries.length
  const series = heroCatalogSeries[active]

  activeRef.current = active

  const measureTab = useCallback((index: number): PillBox | null => {
    const list = listRef.current
    const el = tabRefs.current[index]
    if (!list || !el) return null
    const listRect = list.getBoundingClientRect()
    const btnRect = el.getBoundingClientRect()
    return {
      left: btnRect.left - listRect.left + list.scrollLeft,
      width: btnRect.width,
    }
  }, [])

  const goTo = useCallback(
    (index: number) => {
      progressRef.current = 0
      setProgress(0)
      setActive(((index % count) + count) % count)
    },
    [count]
  )

  const next = useCallback(() => goTo(active + 1), [active, goTo])
  const prev = useCallback(() => goTo(active - 1), [active, goTo])

  useEffect(() => {
    if (paused) return
    if (typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      return
    }

    let frame = 0
    let last = performance.now()

    const tick = (now: number) => {
      const delta = now - last
      last = now
      const nextProgress = Math.min(1, progressRef.current + delta / AUTOPLAY_MS)
      progressRef.current = nextProgress
      setProgress(nextProgress)

      if (nextProgress >= 1) {
        progressRef.current = 0
        setProgress(0)
        setActive((current) => (current + 1) % count)
        return
      }

      frame = window.requestAnimationFrame(tick)
    }

    frame = window.requestAnimationFrame(tick)
    return () => window.cancelAnimationFrame(frame)
  }, [active, paused, count])

  useLayoutEffect(() => {
    const reduced =
      typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches
    const target = measureTab(active)
    if (!target) return

    setPillMotion(!reduced && pillReady)
    setPill(target)
    setPillReady(true)
  }, [active, measureTab, pillReady])

  useEffect(() => {
    const list = listRef.current
    if (!list) return

    const sync = () => {
      const box = measureTab(activeRef.current)
      if (!box) return
      setPillMotion(false)
      setPill(box)
    }

    const observer = new ResizeObserver(sync)
    observer.observe(list)
    window.addEventListener('resize', sync)
    return () => {
      observer.disconnect()
      window.removeEventListener('resize', sync)
    }
  }, [measureTab])

  return (
    <section className="relative overflow-hidden bg-[#f5f4f1]">
      <div
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_72%_28%,rgba(255,255,255,0.85),transparent_58%),linear-gradient(168deg,#f7f6f3_0%,#f5f4f1_55%,#efeee9_100%)]"
        aria-hidden
      />

      <div className="relative mx-auto grid max-w-7xl items-center gap-5 px-4 py-5 sm:gap-8 sm:px-6 sm:py-8 lg:grid-cols-[minmax(0,1.02fr)_minmax(0,0.98fr)] lg:gap-8 lg:px-8 lg:py-9">
        <div className="animate-hero-rise min-w-0 text-center lg:text-left">
          <div className="mb-5 hidden min-w-0 items-center justify-center gap-3 sm:mb-6 sm:gap-5 lg:mb-6 lg:flex lg:justify-start">
            <Image
              src="/vedel-logo.png"
              alt="VEDEL"
              width={200}
              height={200}
              priority
              className="h-16 w-auto shrink-0 object-contain sm:h-20 lg:h-24"
              style={{ width: 'auto' }}
            />
            <span className="h-10 w-px shrink-0 bg-neutral-300 sm:h-14 lg:h-16" aria-hidden />
            <Image
              src="/mhi-logo.png"
              alt="Mitsubishi Heavy Industries"
              width={440}
              height={64}
              priority
              className="h-10 w-auto min-w-0 max-w-[min(100%,14rem)] object-contain object-left sm:h-14 sm:max-w-[20rem] lg:h-16 lg:max-w-[24rem]"
              style={{ width: 'auto' }}
            />
          </div>

          <h1 className="mb-3 font-display text-[2.15rem] font-normal leading-[1.12] tracking-wide text-neutral-900 sm:text-[2.75rem] lg:text-[3.25rem]">
            Bursa&apos;da Japon
            <span className="mt-1 block text-red-600">iklimlendirme</span>
          </h1>

          <p className="mx-auto mb-5 max-w-md text-base leading-relaxed text-neutral-600 sm:mb-6 sm:text-lg lg:mx-0">
            Bursa&apos;da Mitsubishi Heavy Industries ve Euroform yetkili bayisiyiz.
            Split, multi, profesyonel ve VRF sistemlerde satış, montaj, bakım ve servis sunuyoruz.
          </p>

          <div className="flex flex-col items-stretch gap-3 sm:flex-row sm:items-center sm:justify-center lg:justify-start">
            <Link
              href="/klimani-sec"
              className="group inline-flex items-center justify-center gap-2 rounded-md bg-red-600 px-7 py-3.5 text-base font-bold text-white transition-colors hover:bg-red-700"
            >
              Klimanı Seç
              <ArrowRight className="h-5 w-5 transition-transform group-hover:translate-x-0.5" />
            </Link>
            <Link
              href="/iletisim"
              className="inline-flex items-center justify-center gap-2 rounded-md border border-neutral-300 bg-white/80 px-7 py-3.5 text-base font-semibold text-neutral-800 transition-colors hover:border-neutral-400 hover:bg-white"
            >
              İletişim
            </Link>
          </div>
        </div>

        <div className="min-w-0">
          <div className="relative mx-auto w-full max-w-xl lg:max-w-none">
            <div className="relative overflow-hidden rounded-2xl border border-neutral-200/80 bg-[#f5f4f1] shadow-[0_24px_50px_-28px_rgba(40,35,30,0.18)] sm:rounded-3xl">
              <div
                ref={listRef}
                role="tablist"
                aria-label="Klima serileri"
                className="relative grid grid-cols-4 border-b border-neutral-200/80"
              >
                <span
                  aria-hidden
                  className="pointer-events-none absolute inset-y-0 bg-red-600"
                  style={{
                    left: pill.left,
                    width: pill.width,
                    opacity: pillReady ? 1 : 0,
                    transition: pillMotion
                      ? `left ${PILL_MS}ms cubic-bezier(0.22, 1, 0.36, 1), width ${PILL_MS}ms cubic-bezier(0.22, 1, 0.36, 1)`
                      : 'none',
                  }}
                />
                {heroCatalogSeries.map((item, index) => {
                  const isActive = index === active
                  return (
                    <button
                      key={item.id}
                      ref={(node) => {
                        tabRefs.current[index] = node
                      }}
                      type="button"
                      role="tab"
                      aria-selected={isActive}
                      onClick={() => goTo(index)}
                      className={`relative z-10 px-0.5 py-2.5 text-center text-[11px] font-semibold transition-colors duration-200 sm:px-1 sm:py-3 sm:text-sm ${
                        isActive
                          ? 'text-white'
                          : 'text-neutral-500 hover:bg-white/40 hover:text-neutral-800'
                      } ${index > 0 ? 'border-l border-neutral-200/70' : ''}`}
                    >
                      {item.name.replace(' Serisi', '')}
                    </button>
                  )
                })}
              </div>

              <div
                className="relative aspect-[2/1] w-full sm:aspect-[16/10] lg:aspect-[4/3]"
                onMouseEnter={() => setPaused(true)}
                onMouseLeave={() => setPaused(false)}
              >
                <div key={series.id} className="absolute inset-0 animate-catalog-product">
                  <Image
                    src={series.image}
                    alt={series.imageAlt}
                    fill
                    priority={active === 0}
                    sizes="(max-width: 1024px) 90vw, 48vw"
                    unoptimized
                    className="object-contain object-center p-4 sm:p-6 lg:p-8"
                  />
                </div>
              </div>

              <div className="h-[2px] w-full overflow-hidden bg-neutral-200/80" aria-hidden>
                <div
                  className="h-full bg-red-600"
                  style={{ width: `${progress * 100}%` }}
                />
              </div>

              <div className="bg-white/70 px-3 py-3 sm:px-5">
                <div key={series.id} className="animate-catalog-crossfade mb-2.5 sm:mb-3">
                  <div className="mb-1 flex flex-wrap items-baseline gap-x-2 gap-y-0.5">
                    <p className="text-sm font-bold text-neutral-900 sm:text-base">{series.name}</p>
                    <p className="text-xs text-neutral-500">{series.brand}</p>
                  </div>
                  <p className="mb-1.5 text-xs text-neutral-600 sm:mb-2 sm:text-sm">{series.tagline}</p>
                  <ul className="flex flex-wrap gap-1.5">
                    {series.features.map((feature) => (
                      <li
                        key={feature}
                        className="rounded-md border border-neutral-300/80 bg-white px-2 py-1 text-[11px] font-semibold text-neutral-800 sm:text-xs"
                      >
                        {feature}
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="flex items-center justify-between gap-2 sm:gap-3">
                  <Link
                    href={series.href}
                    className="group inline-flex items-center gap-1.5 rounded-md bg-red-600 px-3.5 py-2 text-sm font-bold text-white transition-colors hover:bg-red-700 sm:px-4 sm:py-2.5"
                  >
                    Seriyi incele
                    <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
                  </Link>

                  <div className="flex items-center gap-1.5 sm:gap-2">
                    <button
                      type="button"
                      onClick={(event) => {
                        prev()
                        event.currentTarget.blur()
                      }}
                      aria-label="Önceki seri"
                      className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-neutral-200 bg-white text-neutral-700 transition-colors hover:border-neutral-300 hover:bg-neutral-50 sm:h-10 sm:w-10"
                    >
                      <ChevronLeft className="h-5 w-5" />
                    </button>
                    <button
                      type="button"
                      onClick={(event) => {
                        next()
                        event.currentTarget.blur()
                      }}
                      aria-label="Sonraki seri"
                      className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-neutral-200 bg-white text-neutral-700 transition-colors hover:border-neutral-300 hover:bg-neutral-50 sm:h-10 sm:w-10"
                    >
                      <ChevronRight className="h-5 w-5" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
