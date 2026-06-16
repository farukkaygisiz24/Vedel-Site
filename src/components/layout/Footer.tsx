'use client'

import type { ReactNode } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { Phone, Mail, MapPin, ArrowRight } from 'lucide-react'

const PHONE_NUMBERS = [
  { href: 'tel:+902244132416', label: '(0224) 413 24 16' },
  { href: 'tel:+902244132417', label: '(0224) 413 24 17' },
] as const

const QUICK_LINKS = [
  { name: 'Ana Sayfa', href: '/' },
  { name: 'Klimanı Seç', href: '/klimani-sec' },
  { name: 'Hakkımızda', href: '/hakkimizda' },
  { name: 'İletişim', href: '/iletisim' },
  { name: 'Gizlilik Politikası', href: '/gizlilik-politikasi' },
  { name: 'KVKK Aydınlatma Metni', href: '/kvkk' },
  { name: 'Çerez Politikası', href: '/cerez-politikasi' },
  { name: 'VRF Bayisi', href: 'https://www.2vklima.com' },
] as const

const BRANCHES = [
  {
    name: 'Kayapa Bayi',
    address: '30 Ağustos Zafer Mah. Bozyaka Cad. NO:11/CA Nilüfer / Bursa',
  },
  {
    name: 'Özlüce Bayi',
    address: 'Altınşehir Mah. Uğur Mumcu BLV. NO:58/E Nilüfer / Bursa',
  },
] as const

function PhoneLink({ href, label }: { href: string; label: string }) {
  return (
    <a
      href={href}
      className="inline-flex items-center gap-1.5 text-gray-200 transition-colors hover:text-white"
    >
      <Phone className="h-4 w-4 shrink-0 text-red-400 sm:h-5 sm:w-5" />
      <span className="whitespace-nowrap text-sm tabular-nums sm:text-base">{label}</span>
    </a>
  )
}

function PhoneNumbersRow() {
  return (
    <div className="flex w-full items-center justify-start gap-x-3 tabular-nums sm:gap-x-4">
      <PhoneLink href={PHONE_NUMBERS[0].href} label={PHONE_NUMBERS[0].label} />
      <span className="shrink-0 text-white/20" aria-hidden="true">
        |
      </span>
      <PhoneLink href={PHONE_NUMBERS[1].href} label={PHONE_NUMBERS[1].label} />
    </div>
  )
}

function SectionHeading({ children }: { children: ReactNode }) {
  return (
    <h3 className="mb-4 text-lg font-bold text-white sm:mb-6">
      <span className="relative inline-block pb-2 after:absolute after:bottom-0 after:left-0 after:h-0.5 after:w-8 after:rounded-full after:bg-red-500">
        {children}
      </span>
    </h3>
  )
}

type WindWaveProps = {
  top: string
  widthClass: string
  delay: string
  duration: string
  gradientId: string
  path: string
  stops: { offset: string; color: string; opacity: number }[]
}

function WindWave({
  top,
  widthClass,
  delay,
  duration,
  gradientId,
  path,
  stops,
}: WindWaveProps) {
  return (
    <svg
      className={`footer-wind-wave absolute left-0 ${widthClass}`}
      style={{ top, animationDelay: delay, animationDuration: duration }}
      viewBox="0 0 480 28"
      preserveAspectRatio="none"
      aria-hidden="true"
    >
      <defs>
        <linearGradient id={gradientId} x1="0%" y1="0%" x2="100%" y2="0%">
          {stops.map((stop) => (
            <stop
              key={stop.offset}
              offset={stop.offset}
              stopColor={stop.color}
              stopOpacity={stop.opacity}
            />
          ))}
        </linearGradient>
      </defs>
      <path
        d={path}
        fill="none"
        stroke={`url(#${gradientId})`}
        strokeWidth="1.5"
        strokeLinecap="round"
        vectorEffect="non-scaling-stroke"
      />
    </svg>
  )
}

const WIND_WAVES: Omit<WindWaveProps, 'top'>[] = [
  {
    widthClass: 'w-[42%]',
    delay: '0s',
    duration: '11s',
    gradientId: 'footer-wind-wave-red',
    path: 'M0,14 C40,6 80,22 120,14 S200,6 240,14 S320,22 360,14 S440,6 480,14',
    stops: [
      { offset: '0%', color: '#f87171', opacity: 0 },
      { offset: '45%', color: '#f87171', opacity: 0.65 },
      { offset: '55%', color: '#fca5a5', opacity: 0.7 },
      { offset: '100%', color: '#f87171', opacity: 0 },
    ],
  },
  {
    widthClass: 'w-[36%]',
    delay: '3.8s',
    duration: '13s',
    gradientId: 'footer-wind-wave-white',
    path: 'M0,14 C30,20 60,8 90,14 S150,20 180,14 S240,8 270,14 S330,20 360,14 S420,8 480,14',
    stops: [
      { offset: '0%', color: '#ffffff', opacity: 0 },
      { offset: '50%', color: '#ffffff', opacity: 0.38 },
      { offset: '100%', color: '#ffffff', opacity: 0 },
    ],
  },
  {
    widthClass: 'w-[48%]',
    delay: '7.2s',
    duration: '10s',
    gradientId: 'footer-wind-wave-soft',
    path: 'M0,14 C50,4 100,24 150,14 S250,4 300,14 S400,24 450,14 S470,10 480,14',
    stops: [
      { offset: '0%', color: '#fca5a5', opacity: 0 },
      { offset: '42%', color: '#fca5a5', opacity: 0.55 },
      { offset: '58%', color: '#f87171', opacity: 0.6 },
      { offset: '100%', color: '#fca5a5', opacity: 0 },
    ],
  },
]

function FooterBackground() {
  return (
    <div className="footer-animated-bg pointer-events-none absolute inset-0 overflow-hidden" aria-hidden="true">
      <div className="footer-bg-mesh absolute inset-0 bg-[radial-gradient(ellipse_at_18%_45%,rgba(220,38,38,0.22)_0%,transparent_55%),radial-gradient(ellipse_at_82%_78%,rgba(185,28,28,0.18)_0%,transparent_45%),radial-gradient(ellipse_at_58%_12%,rgba(248,113,113,0.12)_0%,transparent_50%)]" />

      <div className="footer-grid-pattern absolute inset-0 opacity-[0.08] bg-[length:60px_60px] bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmZmZmYiIGZpbGwtb3BhY2l0eT0iMSI+PHBhdGggZD0iMzYgMzR2LTRoLTR2NGg0em0wLTh2LTRoLTR2NGg0em0wLTh2LTRoLTR2NGg0em0wLThWMmgtNHY0aDR6TTYgMzR2LTRIMnY0aDR6bTAtOHYtNEgydjRoNHptMC04di00SDJ2NGg0em0wLThWMkgydjRoNHoiLz48L2c+PC9nPjwvc3ZnPg==')]" />

      <div className="footer-orb-a absolute -right-16 -top-16">
        <div className="footer-orb-inner h-80 w-80 rounded-full bg-red-500/20 blur-3xl" />
      </div>
      <div className="footer-orb-b absolute -bottom-32 -left-20">
        <div className="footer-orb-inner h-96 w-96 rounded-full bg-red-600/25 blur-3xl" />
      </div>
      <div className="footer-orb-c absolute left-1/2 top-1/4 -translate-x-1/2">
        <div className="footer-orb-inner h-64 w-64 rounded-full bg-red-400/15 blur-3xl" />
      </div>

      <div className="footer-light-sweep absolute inset-y-0 -left-1/3 w-2/3" />

      <div className="absolute inset-0">
        <WindWave top="23%" {...WIND_WAVES[0]} />
        <WindWave top="49%" {...WIND_WAVES[1]} />
        <WindWave top="77%" {...WIND_WAVES[2]} />
      </div>
    </div>
  )
}

export default function Footer() {
  return (
    <footer className="relative overflow-hidden bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      <FooterBackground />
      <div
        className="footer-accent-bar pointer-events-none absolute inset-x-0 top-0 z-10 h-1.5"
        aria-hidden="true"
      />
      <div className="container relative z-10 mx-auto px-4 py-10 sm:px-6 sm:py-12 lg:py-16">
        <div className="grid grid-cols-1 gap-8 sm:gap-10 md:grid-cols-2 lg:grid-cols-3 lg:gap-12">
          <div>
            <div className="mb-4 flex items-center gap-2.5">
              <div className="relative h-16 w-16 shrink-0 rounded-lg bg-white p-1.5 shadow-md sm:h-[5.25rem] sm:w-[5.25rem]">
                <Image
                  src="/vedel-logo.png"
                  alt="Vedel Klima"
                  fill
                  sizes="(max-width: 640px) 64px, 84px"
                  className="object-contain"
                />
              </div>
              <span className="text-lg font-bold leading-tight text-white">Vedel Klima</span>
            </div>
            <p className="mb-6 max-w-prose text-sm leading-relaxed text-gray-400">
              Mitsubishi Heavy Industries ve Euroform yetkili bayisi olarak iklimlendirme ihtiyaçlarınızda profesyonel çözümler sunuyoruz.
            </p>
            <div className="flex items-center gap-2 text-sm text-gray-300">
              <span className="h-2 w-2 shrink-0 rounded-full bg-red-500 animate-pulse" />
              <span>Yetkili Satış ve Servis Bayi</span>
            </div>
            <div className="mt-2 flex items-center gap-2 text-sm text-gray-300">
              <span className="h-2 w-2 shrink-0 rounded-full bg-red-500 animate-pulse" />
              <span>Bakım ve Onarım Hizmetleri</span>
            </div>
          </div>

          <div className="border-t border-white/10 pt-8 md:border-t-0 md:pt-0">
            <SectionHeading>Hızlı Linkler</SectionHeading>
            <ul className="grid grid-cols-2 gap-x-4 gap-y-3 sm:grid-cols-1">
              {QUICK_LINKS.map((link) => {
                const className =
                  'group flex items-center gap-2 text-sm text-gray-400 transition-colors hover:text-red-400 sm:text-base'
                const content = (
                  <>
                    <ArrowRight className="h-3 w-3 shrink-0 text-red-500 opacity-0 transition-opacity group-hover:opacity-100" />
                    {link.name}
                  </>
                )

                return (
                  <li key={link.name}>
                    {link.href.startsWith('http') ? (
                      <a
                        href={link.href}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={className}
                      >
                        {content}
                      </a>
                    ) : (
                      <Link href={link.href} className={className}>
                        {content}
                      </Link>
                    )}
                  </li>
                )
              })}
            </ul>
          </div>

          <div className="border-t border-white/10 pt-8 md:col-span-2 md:border-t md:pt-8 lg:col-span-1 lg:border-t-0 lg:pt-0">
            <SectionHeading>İletişim</SectionHeading>
            <ul className="space-y-4">
              <li className="w-full">
                <PhoneNumbersRow />
              </li>
              <li className="flex items-start gap-3">
                <Mail className="mt-0.5 h-5 w-5 shrink-0 text-red-400" />
                <div className="min-w-0">
                  <a
                    href="mailto:vedel@vedel.com.tr"
                    className="break-all text-sm text-gray-200 transition-colors hover:text-white sm:text-base sm:break-normal"
                  >
                    vedel@vedel.com.tr
                  </a>
                </div>
              </li>
              {BRANCHES.map((branch) => (
                <li key={branch.name} className="flex items-start gap-3">
                  <MapPin className="mt-0.5 h-5 w-5 shrink-0 text-red-400" />
                  <div className="min-w-0 text-sm break-words text-gray-400">
                    <p className="font-semibold text-gray-200">{branch.name}</p>
                    <p>{branch.address}</p>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      <div className="relative z-10 border-t border-white/10 bg-black/20">
        <div className="container mx-auto px-4 py-5 sm:px-6 sm:py-6">
          <div className="flex flex-col items-center gap-3 text-center sm:flex-row sm:justify-between sm:gap-4 sm:text-left">
            <p className="text-xs text-gray-500 sm:text-sm">
              © {new Date().getFullYear()} Vedel Klima LTD. ŞTİ. Tüm hakları saklıdır.
            </p>
            <a
              href="mailto:farukkaygisiz24@gmail.com"
              className="text-xs text-gray-600 transition-colors hover:text-gray-400 sm:text-sm"
            >
              Build by farukkaygisiz24
            </a>
          </div>
        </div>
      </div>
    </footer>
  )
}
