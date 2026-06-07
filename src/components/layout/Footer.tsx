'use client'

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
      className="inline-flex items-center gap-1.5 text-gray-700 transition-colors hover:text-gray-900"
    >
      <Phone className="h-4 w-4 shrink-0 text-red-600 sm:h-5 sm:w-5" />
      <span className="whitespace-nowrap text-sm tabular-nums sm:text-base">{label}</span>
    </a>
  )
}

function PhoneNumbersRow() {
  return (
    <div className="flex w-full items-center justify-start gap-x-3 tabular-nums sm:gap-x-4">
      <PhoneLink href={PHONE_NUMBERS[0].href} label={PHONE_NUMBERS[0].label} />
      <span className="shrink-0 text-gray-300" aria-hidden="true">
        |
      </span>
      <PhoneLink href={PHONE_NUMBERS[1].href} label={PHONE_NUMBERS[1].label} />
    </div>
  )
}

export default function Footer() {
  return (
    <footer className="bg-white">
      <div className="container mx-auto px-4 py-10 sm:px-6 sm:py-12 lg:py-16">
        <div className="grid grid-cols-1 gap-8 sm:gap-10 md:grid-cols-2 lg:grid-cols-3 lg:gap-12">
          <div>
            <div className="mb-4 flex items-center gap-2.5">
              <div className="relative h-16 w-16 shrink-0 rounded-lg bg-gray-100 p-1.5 sm:h-[5.25rem] sm:w-[5.25rem]">
                <Image
                  src="/vedel-logo.png"
                  alt="Vedel Klima"
                  fill
                  sizes="(max-width: 640px) 64px, 84px"
                  className="object-contain"
                />
              </div>
              <span className="text-lg font-bold leading-tight text-gray-900">Vedel Klima</span>
            </div>
            <p className="mb-6 max-w-prose text-sm leading-relaxed text-gray-600">
              Mitsubishi Heavy Industries ve Euroform yetkili bayisi olarak iklimlendirme ihtiyaçlarınızda profesyonel çözümler sunuyoruz.
            </p>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <span className="h-2 w-2 shrink-0 rounded-full bg-red-600 animate-pulse" />
              <span>Yetkili Satış ve Servis Bayi</span>
            </div>
            <div className="mt-2 flex items-center gap-2 text-sm text-gray-600">
              <span className="h-2 w-2 shrink-0 rounded-full bg-red-600 animate-pulse" />
              <span>Bakım ve Onarım Hizmetleri</span>
            </div>
          </div>

          <div className="border-t border-gray-100 pt-8 md:border-t-0 md:pt-0">
            <h3 className="mb-4 text-lg font-bold text-gray-900 sm:mb-6">Hızlı Linkler</h3>
            <ul className="grid grid-cols-2 gap-x-4 gap-y-3 sm:grid-cols-1">
              {QUICK_LINKS.map((link) => {
                const className =
                  'group flex items-center gap-2 text-sm text-gray-600 transition-colors hover:text-red-600 sm:text-base'
                const content = (
                  <>
                    <ArrowRight className="h-3 w-3 shrink-0 text-red-600 opacity-0 transition-opacity group-hover:opacity-100" />
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

          <div className="border-t border-gray-100 pt-8 md:col-span-2 md:border-t md:pt-8 lg:col-span-1 lg:border-t-0 lg:pt-0">
            <h3 className="mb-4 text-lg font-bold text-gray-900 sm:mb-6">İletişim</h3>
            <ul className="space-y-4">
              <li className="w-full">
                <PhoneNumbersRow />
              </li>
              <li className="flex items-start gap-3">
                <Mail className="mt-0.5 h-5 w-5 shrink-0 text-red-600" />
                <div className="min-w-0">
                  <a
                    href="mailto:vedel@vedel.com.tr"
                    className="break-all text-sm text-gray-700 transition-colors hover:text-gray-900 sm:text-base sm:break-normal"
                  >
                    vedel@vedel.com.tr
                  </a>
                </div>
              </li>
              {BRANCHES.map((branch) => (
                <li key={branch.name} className="flex items-start gap-3">
                  <MapPin className="mt-0.5 h-5 w-5 shrink-0 text-red-600" />
                  <div className="min-w-0 text-sm break-words text-gray-600">
                    <p className="font-semibold text-gray-800">{branch.name}</p>
                    <p>{branch.address}</p>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      <div className="border-t border-gray-200">
        <div className="container mx-auto px-4 py-5 sm:px-6 sm:py-6">
          <div className="flex flex-col items-center gap-3 text-center sm:flex-row sm:justify-between sm:gap-4 sm:text-left">
            <p className="text-xs text-gray-500 sm:text-sm">
              © {new Date().getFullYear()} Vedel Klima LTD. ŞTİ. Tüm hakları saklıdır.
            </p>
            <a
              href="mailto:farukkaygisiz24@gmail.com"
              className="text-xs text-gray-400 transition-colors hover:text-gray-600 sm:text-sm"
            >
              Build by farukkaygisiz24
            </a>
          </div>
        </div>
      </div>
    </footer>
  )
}
