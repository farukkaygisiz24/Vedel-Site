'use client'

import { useState, useRef, useEffect } from 'react'
import { createPortal } from 'react-dom'
import Link from 'next/link'
import Image from 'next/image'
import { Phone, Menu, X, ArrowRight, ChevronDown } from 'lucide-react'

const productsMenu = [
  {
    brand: 'MHI',
    logo: '/mhi-logo.png',
    logoWidth: 220,
    logoHeight: 32,
    categories: [
      { name: 'Split Sistemler', href: '/urunler/splitsistemler/mhi' },
      { name: 'Multi Sistemler', href: '/urunler/multisistemler/mhi' },
      { name: 'Profesyonel Sistemler', href: '/urunler/profesyonelsistemler/mhi' },
    ]
  },
  {
    brand: 'Euroform',
    logo: '/euroform.png',
    logoWidth: 88,
    logoHeight: 32,
    categories: [
      { name: 'Split Sistemler', href: '/urunler/splitsistemler/euroform' },
      { name: 'Multi Sistemler', href: '/urunler/multisistemler/euroform' },
      { name: 'Profesyonel Sistemler', href: '/urunler/profesyonelsistemler/euroform' },
    ]
  }
]

const mainNav = [
  { name: 'Ana Sayfa', href: '/' },
  { name: 'Hakkımızda', href: '/hakkimizda' },
]

const navItems = [
  { name: 'Klimanı Seç', href: '/klimani-sec' },
  { name: 'İletişim', href: '/iletisim' },
]

const MOBILE_BREAKPOINT = 1024
const SWIPE_EDGE_ZONE = 32
const SWIPE_MIN_DISTANCE = 56

export default function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const [productsOpen, setProductsOpen] = useState(false)
  const [dropdownTimeout, setDropdownTimeout] = useState<NodeJS.Timeout | null>(null)
  const [mounted, setMounted] = useState(false)
  const edgeSwipeStartRef = useRef<{ x: number; y: number } | null>(null)
  const panelSwipeStartRef = useRef<{ x: number; y: number } | null>(null)

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setMounted(true)
  }, [])

  // Lock body scroll when mobile menu is open
  useEffect(() => {
    if (mobileMenuOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
    return () => {
      document.body.style.overflow = ''
    }
  }, [mobileMenuOpen])

  useEffect(() => {
    const isMobileViewport = () => window.innerWidth < MOBILE_BREAKPOINT

    const isHorizontalSwipe = (deltaX: number, deltaY: number) =>
      Math.abs(deltaX) > Math.abs(deltaY) * 1.2

    const handleEdgeTouchStart = (event: TouchEvent) => {
      if (!isMobileViewport() || mobileMenuOpen) return

      const touch = event.touches[0]
      if (touch.clientX >= window.innerWidth - SWIPE_EDGE_ZONE) {
        edgeSwipeStartRef.current = { x: touch.clientX, y: touch.clientY }
      }
    }

    const handleEdgeTouchEnd = (event: TouchEvent) => {
      if (!edgeSwipeStartRef.current || !isMobileViewport() || mobileMenuOpen) {
        edgeSwipeStartRef.current = null
        return
      }

      const touch = event.changedTouches[0]
      const deltaX = touch.clientX - edgeSwipeStartRef.current.x
      const deltaY = touch.clientY - edgeSwipeStartRef.current.y
      edgeSwipeStartRef.current = null

      if (deltaX < -SWIPE_MIN_DISTANCE && isHorizontalSwipe(deltaX, deltaY)) {
        setMobileMenuOpen(true)
      }
    }

    document.addEventListener('touchstart', handleEdgeTouchStart, { passive: true })
    document.addEventListener('touchend', handleEdgeTouchEnd, { passive: true })

    return () => {
      document.removeEventListener('touchstart', handleEdgeTouchStart)
      document.removeEventListener('touchend', handleEdgeTouchEnd)
    }
  }, [mobileMenuOpen])

  const handleMouseEnter = () => {
    if (dropdownTimeout) clearTimeout(dropdownTimeout)
    setDropdownOpen(true)
  }

  const handleMouseLeave = () => {
    const timeout = setTimeout(() => setDropdownOpen(false), 300)
    setDropdownTimeout(timeout)
  }

  const closeMobileMenu = () => {
    setMobileMenuOpen(false)
    setProductsOpen(false)
  }

  const handlePanelTouchStart = (event: React.TouchEvent<HTMLDivElement>) => {
    const touch = event.touches[0]
    panelSwipeStartRef.current = { x: touch.clientX, y: touch.clientY }
  }

  const handlePanelTouchEnd = (event: React.TouchEvent<HTMLDivElement>) => {
    if (!panelSwipeStartRef.current) return

    const touch = event.changedTouches[0]
    const deltaX = touch.clientX - panelSwipeStartRef.current.x
    const deltaY = touch.clientY - panelSwipeStartRef.current.y
    panelSwipeStartRef.current = null

    if (
      deltaX > SWIPE_MIN_DISTANCE &&
      Math.abs(deltaX) > Math.abs(deltaY) * 1.2
    ) {
      closeMobileMenu()
    }
  }

  const header = (
    <header className="sticky top-0 z-50 bg-white shadow-sm">
      <div className="container relative mx-auto h-20 max-lg:max-w-none max-lg:px-2.5 sm:max-lg:px-4 md:max-lg:px-6 lg:px-8">

          {/* Desktop Nav — tam ortada (logo/telefon genişliğinden bağımsız) */}
          <nav className="hidden lg:flex absolute left-1/2 top-1/2 z-30 -translate-x-1/2 -translate-y-1/2 items-center">
            <div className="flex items-center gap-2 xl:gap-4 2xl:gap-6">
            {mainNav.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="text-gray-800 hover:text-red-600 font-semibold text-xs lg:text-sm xl:text-base transition-colors duration-300 relative group whitespace-nowrap"
              >
                {item.name}
                <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-red-600 transition-all duration-300 group-hover:w-full" />
              </Link>
            ))}

            <div
              className="relative"
              onMouseEnter={handleMouseEnter}
              onMouseLeave={handleMouseLeave}
            >
              <button className="flex items-center gap-1 text-gray-800 hover:text-red-600 font-semibold text-xs lg:text-sm xl:text-base transition-colors duration-300 relative group whitespace-nowrap">
                Ürünler
                <ChevronDown className={`w-4 h-4 transition-transform duration-300 ${dropdownOpen ? 'rotate-180' : ''}`} />
                <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-red-600 transition-all duration-300 group-hover:w-full" />
              </button>

              <div
                className={`absolute top-full left-1/2 z-40 mt-3 w-[500px] -translate-x-1/2 rounded-xl border border-gray-100 bg-white shadow-2xl overflow-hidden transition-all duration-200 ${
                  dropdownOpen
                    ? 'visible pointer-events-auto opacity-100 animate-[header-dropdown_0.2s_ease-out]'
                    : 'invisible pointer-events-none opacity-0'
                }`}
                aria-hidden={!dropdownOpen}
              >
                <div className="grid grid-cols-2 divide-x divide-gray-100">
                  {productsMenu.map((brand, brandIndex) => (
                    <div key={brandIndex} className="p-4">
                      <div className="flex items-center justify-center mb-3 pb-2 border-b border-gray-100">
                        <Image
                          src={brand.logo}
                          alt={brand.brand}
                          width={brand.logoWidth}
                          height={brand.logoHeight}
                          quality={90}
                          sizes="220px"
                          loading="eager"
                          className="h-8 w-auto object-contain"
                          style={{ width: 'auto' }}
                        />
                      </div>
                      <ul className="space-y-2">
                        {brand.categories.map((cat, catIndex) => (
                          <li key={catIndex}>
                            <Link
                              href={cat.href}
                              className="block py-2 px-3 text-sm text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all duration-200"
                              onClick={() => setDropdownOpen(false)}
                              tabIndex={dropdownOpen ? 0 : -1}
                            >
                              {cat.name}
                            </Link>
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="text-gray-800 hover:text-red-600 font-semibold text-xs lg:text-sm xl:text-base transition-colors duration-300 relative group whitespace-nowrap"
              >
                {item.name}
                <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-red-600 transition-all duration-300 group-hover:w-full" />
              </Link>
            ))}
          </div>
        </nav>

        <div className="relative z-20 grid h-full min-w-0 grid-cols-[minmax(0,1fr)_4.5rem] items-center gap-1 sm:grid-cols-[minmax(0,1fr)_5rem] sm:gap-2 lg:flex lg:justify-between lg:gap-4 pointer-events-none">

          {/* Logo — mobil: grid ile taşma yok | lg+: masaüstü düzeni */}
          <Link
            href="/"
            className="pointer-events-auto flex min-w-0 items-center gap-1.5 sm:gap-2 md:gap-3 lg:max-w-[min(100%,calc(50%-8.5rem))] lg:shrink-0 lg:gap-2 xl:max-w-[min(100%,22rem)] xl:gap-4 2xl:max-w-none"
          >
            <Image
              src="/vedel-logo.png"
              alt="VEDEL"
              width={200}
              height={200}
              priority
              className="h-12 w-auto max-w-[3.75rem] shrink-0 object-contain sm:h-14 sm:max-w-[4.25rem] md:h-16 md:max-w-none lg:h-16 xl:h-[4.5rem]"
              style={{ width: 'auto' }}
              sizes="(max-width: 640px) 52px, (max-width: 1280px) 64px, 72px"
            />
            <span
              className="hidden h-5 w-px shrink-0 bg-gray-200 md:block lg:h-6"
              aria-hidden
            />
            <div className="relative h-11 min-w-0 flex-1 sm:h-12 md:h-[3.25rem] md:max-w-[38vw] lg:h-[3.25rem] lg:w-[11rem] lg:max-w-none lg:flex-none xl:h-[3.375rem] xl:w-[13rem] 2xl:w-[15.625rem]">
              <Image
                src="/mhi-logo.png"
                alt="MHI"
                fill
                priority
                className="object-contain object-left"
                sizes="(max-width: 640px) 60vw, (max-width: 1024px) 38vw, (max-width: 1280px) 176px, (max-width: 1536px) 208px, 250px"
                quality={90}
              />
            </div>
          </Link>

        {/* Sağ aksiyonlar — mobilde sabit sütun genişliği */}
        <div className="flex shrink-0 items-center justify-end gap-0 sm:gap-0.5 md:gap-2 pointer-events-auto lg:gap-2">
          <a
            href="tel:+902244132316"
            className="hidden lg:flex xl:hidden items-center justify-center w-9 h-9 text-red-600 hover:bg-red-50 rounded-full transition-colors"
            aria-label="(0224) 413 23 16"
          >
            <Phone className="w-5 h-5" />
          </a>
          <a
            href="tel:+902244132316"
            className="hidden xl:flex items-center gap-2 text-red-600 font-bold hover:text-red-700 transition-colors whitespace-nowrap"
          >
            <Phone className="w-5 h-5 shrink-0" />
            <span className="text-sm">(0224) 413 23 16</span>
          </a>

          <a
            href="tel:+902244132316"
            className="lg:hidden flex h-8 w-8 items-center justify-center rounded-full text-red-600 active:bg-red-50 sm:h-9 sm:w-9 md:h-10 md:w-10 md:hover:bg-red-50"
            aria-label="(0224) 413 23 16"
          >
            <Phone className="h-5 w-5 md:h-[1.35rem] md:w-[1.35rem]" />
          </a>

          <button
            className="lg:hidden flex h-8 w-8 items-center justify-center rounded-full text-gray-800 active:bg-gray-100 sm:h-9 sm:w-9 md:h-10 md:w-10 md:hover:bg-gray-100"
            onClick={() => setMobileMenuOpen(true)}
            aria-label="Menüyü aç"
          >
            <Menu className="h-5 w-5 sm:h-6 sm:w-6" />
          </button>
        </div>
        </div>
      </div>
    </header>
  )

  // Mobile menu is portaled to document.body so the overlay covers the entire page
  const mobileMenuPortal = mounted && typeof document !== 'undefined' ? createPortal(
    <div
      className={`fixed inset-0 z-[60] transition-opacity duration-300 lg:hidden ${mobileMenuOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'
        }`}
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/70"
        onClick={closeMobileMenu}
      />

      {/* Menu Panel */}
      <div
        onTouchStart={handlePanelTouchStart}
        onTouchEnd={handlePanelTouchEnd}
        className={`absolute right-0 top-0 bottom-0 flex w-[min(100%,20rem)] flex-col bg-white shadow-2xl transition-transform duration-300 ease-out touch-pan-y sm:w-80 md:w-[22rem] ${mobileMenuOpen ? 'translate-x-0' : 'translate-x-full'
          }`}
        style={{ height: '100dvh' }}
      >
        {/* Menu Header */}
        <div className="flex items-center justify-between p-5 border-b border-gray-100">
          <span className="font-bold text-xl text-gray-900">Menü</span>
          <button
            onClick={closeMobileMenu}
            className="p-2 text-gray-700 hover:text-red-600 hover:bg-gray-100 rounded-full transition-colors"
            aria-label="Menüyü kapat"
          >
            <X className="w-7 h-7" />
          </button>
        </div>

        {/* Menu Navigation */}
        <nav className="flex-1 overflow-y-auto overscroll-contain">
          {mainNav.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="flex items-center justify-between py-4 px-5 text-gray-800 hover:text-red-600 hover:bg-red-50 font-medium border-b border-gray-100 active:bg-red-100"
              onClick={closeMobileMenu}
            >
              <span className="text-lg">{item.name}</span>
              <ArrowRight className="w-5 h-5 flex-shrink-0" />
            </Link>
          ))}

          {/* Products Accordion */}
          <div className="border-b border-gray-100">
            <button
              className="flex items-center justify-between w-full py-4 px-5 text-gray-800 hover:text-red-600 hover:bg-red-50 font-medium active:bg-red-100"
              onClick={() => setProductsOpen(!productsOpen)}
            >
              <span className="text-lg">Ürünler</span>
              <ChevronDown className={`w-5 h-5 flex-shrink-0 transition-transform duration-300 ${productsOpen ? 'rotate-180' : ''}`} />
            </button>

            <div
              className={`overflow-hidden transition-all duration-300 ease-in-out ${productsOpen ? 'max-h-[600px] opacity-100' : 'max-h-0 opacity-0'
                }`}
            >
              <div className="pb-4">
                {productsMenu.map((brand, brandIndex) => (
                  <div key={brandIndex} className="mt-3">
                    <div className="flex items-center gap-2 px-5 py-2 bg-gray-50">
                      <Image
                        src={brand.logo}
                        alt={brand.brand}
                        width={brand.logoWidth}
                        height={brand.logoHeight}
                        quality={90}
                        sizes="140px"
                        loading="eager"
                        className="h-6 w-auto object-contain"
                        style={{ width: 'auto' }}
                      />
                    </div>
                    <ul className="mt-1">
                      {brand.categories.map((cat, catIndex) => (
                        <li key={catIndex}>
                          <Link
                            href={cat.href}
                            className="block py-3 px-8 text-gray-600 hover:text-red-600 hover:bg-red-50 active:bg-red-100 transition-colors"
                            onClick={closeMobileMenu}
                          >
                            {cat.name}
                          </Link>
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="flex items-center justify-between py-4 px-5 text-gray-800 hover:text-red-600 hover:bg-red-50 font-medium border-b border-gray-100 active:bg-red-100"
              onClick={closeMobileMenu}
            >
              <span className="text-lg">{item.name}</span>
              <ArrowRight className="w-5 h-5 flex-shrink-0" />
            </Link>
          ))}
        </nav>

        {/* Phone CTA at bottom */}
        <div className="p-5 border-t border-gray-100">
          <a
            href="tel:+902244132316"
            className="flex items-center justify-center gap-3 w-full py-4 bg-red-600 text-white font-bold rounded-xl hover:bg-red-700 active:bg-red-800 transition-colors text-lg"
            onClick={closeMobileMenu}
          >
            <Phone className="w-6 h-6" />
            <span>(0224) 413 23 16</span>
          </a>
        </div>
      </div>
    </div>,
    document.body
  ) : null

  return (
    <>
      {header}
      {mobileMenuPortal}
    </>
  )
}
