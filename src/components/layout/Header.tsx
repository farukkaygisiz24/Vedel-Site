'use client'

import { useState, useRef, useEffect } from 'react'
import { createPortal } from 'react-dom'
import Link from 'next/link'
import Image from 'next/image'
import { gsap } from 'gsap'
import { useGSAP } from '@gsap/react'
import { Phone, Menu, X, ArrowRight, ChevronDown } from 'lucide-react'

const productsMenu = [
  {
    brand: 'MHI',
    logo: '/mhi-logo.png',
    categories: [
      { name: 'Split Sistemler', href: '/urunler/splitsistemler/mhi' },
      { name: 'Multi Sistemler', href: '/urunler/multisistemler/mhi' },
      { name: 'Profesyonel Sistemler', href: '/urunler/profesyonelsistemler/mhi' },
    ]
  },
  {
    brand: 'Euroform',
    logo: '/euroform.png',
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

export default function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const [productsOpen, setProductsOpen] = useState(false)
  const [dropdownTimeout, setDropdownTimeout] = useState<NodeJS.Timeout | null>(null)
  const [mounted, setMounted] = useState(false)
  const headerRef = useRef<HTMLElement>(null)
  const dropdownRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
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

  useGSAP(() => {
    gsap.from(headerRef.current, {
      y: -100,
      opacity: 0,
      duration: 1,
      ease: 'power3.out'
    })
  }, { scope: headerRef })

  useGSAP(() => {
    if (dropdownOpen && dropdownRef.current) {
      gsap.fromTo(dropdownRef.current,
        { y: -10, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.3, ease: 'power3.out' }
      )
    }
  }, [dropdownOpen])

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

  const header = (
    <header ref={headerRef} className="sticky top-0 z-50 bg-white shadow-sm">
      <div className="container mx-auto px-4 h-16 lg:h-20 flex items-center justify-between">

        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 sm:gap-3 flex-shrink-0">
          <Image
            src="/vedel-logo.png"
            alt="VEDEL"
            width={1200}
            height={1200}
            priority
            className="h-10 lg:h-14 w-auto"
          />
          <Image
            src="/mhi-logo.png"
            alt="MHI"
            width={1653}
            height={237}
            priority
            className="h-7 lg:h-10 w-auto"
            quality={100}
          />
        </Link>

        {/* Desktop Nav - hidden below lg (1024px) */}
        <nav className="hidden lg:flex items-center justify-center flex-1 absolute left-1/2 -translate-x-1/2">
          <div className="flex items-center gap-6 xl:gap-8">
            {mainNav.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="text-gray-800 hover:text-red-600 font-semibold text-sm xl:text-base transition-colors duration-300 relative group whitespace-nowrap"
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
              <button className="flex items-center gap-1 text-gray-800 hover:text-red-600 font-semibold text-sm xl:text-base transition-colors duration-300 relative group whitespace-nowrap">
                Ürünler
                <ChevronDown className={`w-4 h-4 transition-transform duration-300 ${dropdownOpen ? 'rotate-180' : ''}`} />
                <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-red-600 transition-all duration-300 group-hover:w-full" />
              </button>

              {dropdownOpen && (
                <div
                  ref={dropdownRef}
                  className="absolute top-full left-1/2 -translate-x-1/2 mt-3 w-[500px] bg-white rounded-xl shadow-2xl border border-gray-100 overflow-hidden"
                >
                  <div className="grid grid-cols-2 divide-x divide-gray-100">
                    {productsMenu.map((brand, brandIndex) => (
                      <div key={brandIndex} className="p-4">
                        <div className="flex items-center justify-center mb-3 pb-2 border-b border-gray-100">
                          <Image
                            src={brand.logo}
                            alt={brand.brand}
                            width={100}
                            height={40}
                            className="h-8 w-auto"
                          />
                        </div>
                        <ul className="space-y-2">
                          {brand.categories.map((cat, catIndex) => (
                            <li key={catIndex}>
                              <Link
                                href={cat.href}
                                className="block py-2 px-3 text-sm text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all duration-200"
                                onClick={() => setDropdownOpen(false)}
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
              )}
            </div>

            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="text-gray-800 hover:text-red-600 font-semibold text-sm xl:text-base transition-colors duration-300 relative group whitespace-nowrap"
              >
                {item.name}
                <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-red-600 transition-all duration-300 group-hover:w-full" />
              </Link>
            ))}
          </div>
        </nav>

        {/* Right side actions */}
        <div className="flex items-center gap-3 lg:gap-4 flex-shrink-0">
          {/* Desktop phone */}
          <a
            href="tel:+902244131617"
            className="hidden lg:flex items-center gap-2 text-red-600 font-bold hover:text-red-700 transition-colors"
          >
            <Phone className="w-5 h-5" />
            <span className="text-sm">(0224) 413 16 17</span>
          </a>

          {/* Mobile phone icon */}
          <a
            href="tel:+902244131617"
            className="lg:hidden flex items-center justify-center w-10 h-10 text-red-600 hover:bg-red-50 rounded-full transition-colors"
          >
            <Phone className="w-6 h-6" />
          </a>

          {/* Mobile menu button */}
          <button
            className="lg:hidden p-2 text-gray-800 hover:bg-gray-100 rounded-full transition-colors"
            onClick={() => setMobileMenuOpen(true)}
            aria-label="Menüyü aç"
          >
            <Menu className="w-7 h-7" />
          </button>
        </div>
      </div>
    </header>
  )

  // Mobile menu is portaled to document.body so backdrop-blur covers the entire page
  const mobileMenuPortal = mounted && typeof document !== 'undefined' ? createPortal(
    <div
      className={`fixed inset-0 z-[60] transition-opacity duration-300 lg:hidden ${mobileMenuOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'
        }`}
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/70 backdrop-blur-lg"
        onClick={closeMobileMenu}
      />

      {/* Menu Panel */}
      <div
        className={`absolute right-0 top-0 bottom-0 w-80 max-w-[85vw] bg-white shadow-2xl flex flex-col transition-transform duration-300 ease-out ${mobileMenuOpen ? 'translate-x-0' : 'translate-x-full'
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
                        width={60}
                        height={24}
                        className="h-6 w-auto"
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
            href="tel:+902244131617"
            className="flex items-center justify-center gap-3 w-full py-4 bg-red-600 text-white font-bold rounded-xl hover:bg-red-700 active:bg-red-800 transition-colors text-lg"
            onClick={closeMobileMenu}
          >
            <Phone className="w-6 h-6" />
            <span>(0224) 413 16 17</span>
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
