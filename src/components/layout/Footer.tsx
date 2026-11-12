import type { ReactNode } from 'react'
import Link from 'next/link'
import Image from 'next/image'

const PHONES = [
  { href: 'tel:+902244132416', label: '(0224) 413 24 16' },
  { href: 'tel:+902244132417', label: '(0224) 413 24 17' },
] as const

const PRODUCT_LINKS = [
  { name: 'Split Sistemler', href: '/urunler/splitsistemler' },
  { name: 'Multi Sistemler', href: '/urunler/multisistemler' },
  { name: 'Profesyonel Sistemler', href: '/urunler/profesyonelsistemler' },
  { name: 'VRF Sistemler', href: '/urunler/vrfsistemler' },
] as const

const COMPANY_LINKS = [
  { name: 'Ana Sayfa', href: '/' },
  { name: 'Hakkımızda', href: '/hakkimizda' },
  { name: 'Klimanı Seç', href: '/klimani-sec' },
  { name: 'İletişim', href: '/iletisim' },
] as const

const LEGAL_LINKS = [
  { name: 'Gizlilik Politikası', href: '/gizlilik-politikasi' },
  { name: 'KVKK', href: '/kvkk' },
  { name: 'Çerez Politikası', href: '/cerez-politikasi' },
] as const

const BRANCHES = [
  {
    name: 'Kayapa',
    address: '30 Ağustos Zafer Mah. Bozyaka Cad. No:11/CA Nilüfer / Bursa',
  },
  {
    name: 'Özlüce',
    address: 'Altınşehir Mah. Uğur Mumcu Blv. No:58/E Nilüfer / Bursa',
  },
] as const

function FooterLink({
  href,
  children,
  external,
}: {
  href: string
  children: ReactNode
  external?: boolean
}) {
  const className =
    'text-sm text-neutral-400 transition-colors hover:text-white'

  if (external) {
    return (
      <a href={href} target="_blank" rel="noopener noreferrer" className={className}>
        {children}
      </a>
    )
  }

  return (
    <Link href={href} className={className}>
      {children}
    </Link>
  )
}

export default function Footer() {
  const year = new Date().getFullYear()

  return (
    <footer className="border-t border-neutral-800 bg-neutral-950 text-neutral-300">
      <div className="mx-auto max-w-7xl px-4 py-14 sm:px-6 lg:px-8 lg:py-16">
        <div className="grid grid-cols-1 gap-12 md:grid-cols-2 lg:grid-cols-12 lg:gap-10">
          <div className="lg:col-span-4">
            <div className="mb-5 flex items-center gap-3">
              <div className="relative h-14 w-14 shrink-0 overflow-hidden rounded-md bg-white p-1.5">
                <Image
                  src="/vedel-logo.png"
                  alt="Vedel Klima"
                  fill
                  sizes="56px"
                  className="object-contain"
                />
              </div>
              <div>
                <p className="text-base font-bold text-white">Vedel Klima</p>
                <p className="text-xs tracking-wide text-neutral-500">
                  MHI & Euroform Yetkili Bayi
                </p>
              </div>
            </div>
            <p className="max-w-sm text-sm leading-relaxed text-neutral-400">
              Bursa&apos;da 25 yılı aşkın tecrübeyle Mitsubishi Heavy Industries ve
              Euroform ürünlerinde satış, montaj, bakım ve yetkili servis
              sunuyoruz. Konuttan ticari tesise kadar doğru iklimlendirme çözümü
              için yanınızdayız.
            </p>
            <a
              href="https://www.2vklima.com"
              target="_blank"
              rel="noopener noreferrer"
              className="mt-5 inline-flex text-sm font-medium text-red-400 transition-colors hover:text-red-300"
            >
              VRF sitemiz: 2vklima.com
            </a>
          </div>

          <div className="lg:col-span-2">
            <h3 className="mb-4 text-xs font-semibold tracking-[0.18em] text-white uppercase">
              Sistemler
            </h3>
            <ul className="space-y-3">
              {PRODUCT_LINKS.map((link) => (
                <li key={link.href}>
                  <FooterLink href={link.href}>{link.name}</FooterLink>
                </li>
              ))}
            </ul>
          </div>

          <div className="lg:col-span-2">
            <h3 className="mb-4 text-xs font-semibold tracking-[0.18em] text-white uppercase">
              Kurumsal
            </h3>
            <ul className="space-y-3">
              {COMPANY_LINKS.map((link) => (
                <li key={link.href}>
                  <FooterLink href={link.href}>{link.name}</FooterLink>
                </li>
              ))}
            </ul>
          </div>

          <div className="lg:col-span-4">
            <h3 className="mb-4 text-xs font-semibold tracking-[0.18em] text-white uppercase">
              İletişim
            </h3>
            <ul className="space-y-4 text-sm">
              <li className="flex flex-wrap gap-x-3 gap-y-1">
                {PHONES.map((phone, index) => (
                  <span key={phone.href} className="inline-flex items-center gap-3">
                    {index > 0 && (
                      <span className="text-neutral-700" aria-hidden>
                        |
                      </span>
                    )}
                    <a
                      href={phone.href}
                      className="tabular-nums text-neutral-200 transition-colors hover:text-white"
                    >
                      {phone.label}
                    </a>
                  </span>
                ))}
              </li>
              <li>
                <a
                  href="mailto:vedel@vedel.com.tr"
                  className="text-neutral-200 transition-colors hover:text-white"
                >
                  vedel@vedel.com.tr
                </a>
              </li>
              {BRANCHES.map((branch) => (
                <li key={branch.name}>
                  <p className="font-medium text-neutral-200">{branch.name}</p>
                  <p className="mt-0.5 leading-relaxed text-neutral-500">{branch.address}</p>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      <div className="border-t border-neutral-800">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-5 sm:flex-row sm:items-center sm:justify-between sm:px-6 lg:px-8">
          <p className="text-xs text-neutral-500">
            © {year} Vedel Klima LTD. ŞTİ. Tüm hakları saklıdır.
          </p>
          <nav className="flex flex-wrap items-center gap-x-4 gap-y-2" aria-label="Yasal">
            {LEGAL_LINKS.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="text-xs text-neutral-500 transition-colors hover:text-neutral-300"
              >
                {link.name}
              </Link>
            ))}
            <a
              href="mailto:farukkaygisiz24@gmail.com"
              className="text-xs text-neutral-600 transition-colors hover:text-neutral-400"
            >
              Build by farukkaygisiz24
            </a>
          </nav>
        </div>
      </div>
    </footer>
  )
}
