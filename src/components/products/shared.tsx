'use client'

import Image from 'next/image'
import Link from 'next/link'
import { ArrowLeft, Snowflake, Flame, Zap, Wind, Clock, Shield, Star, Calculator } from 'lucide-react'
import PriceDisplay from '@/components/ui/PriceDisplay'
import FilterSidebar from '@/components/ui/FilterSidebar'
import MultiPriceNotice from '@/components/products/MultiPriceNotice'
import { ACCENT_THEME, formatBtu, type ProductAccent } from '@/components/products/productTheme'

export type { ProductAccent } from '@/components/products/productTheme'

export interface ListingProduct {
  id: string
  model: string
  name: string
  btu: number
  energyClass: string
  coolingCapacity: string
  heatingCapacity: string
  image: string
}

export function ProductCard({
  product,
  brand,
  accent,
}: {
  product: ListingProduct
  brand: string
  accent: ProductAccent
}) {
  const modelParam = product.model.replace('-SET', '')
  const theme = ACCENT_THEME[accent]

  return (
    <Link href={`/urunler/${brand}/${modelParam}`} className="block h-full">
      <div className="group flex h-full flex-col overflow-hidden rounded-2xl border border-gray-100 bg-white shadow-sm transition-all duration-300 md:hover:-translate-y-1 md:hover:shadow-xl">
        <div className="flex h-40 items-center justify-center bg-gray-50 p-3 sm:h-48 sm:p-4">
          <Image
            src={product.image}
            alt={product.model}
            width={320}
            height={200}
            sizes="(max-width: 640px) 90vw, (max-width: 1024px) 45vw, 320px"
            quality={90}
            className="h-full w-auto max-w-full object-contain transition-transform duration-300 md:group-hover:scale-105"
          />
        </div>
        <div className="flex flex-1 flex-col p-4 sm:p-6">
          <div className="mb-4 flex items-start justify-between gap-3">
            <div className="min-w-0">
              <span className={`mb-2 inline-block rounded-full px-3 py-1 text-xs font-bold ${theme.badge}`}>
                {formatBtu(product.btu)}
              </span>
              <h3 className="text-base font-bold text-gray-900 sm:text-lg">{product.model}</h3>
              <p className="text-sm text-gray-500">{product.name}</p>
            </div>
            <div className="flex shrink-0 items-center gap-1 rounded-lg bg-green-100 px-2 py-1 text-green-700">
              <Zap className="h-4 w-4" />
              <span className="text-sm font-bold">{product.energyClass}</span>
            </div>
          </div>

          <div className="mb-4 grid grid-cols-2 gap-2 sm:gap-3">
            <div className="flex items-center gap-2 text-xs text-gray-600 sm:text-sm">
              <Snowflake className="h-4 w-4 shrink-0 text-blue-500" />
              <span>Soğutma</span>
            </div>
            <div className="flex items-center gap-2 text-xs text-gray-600 sm:text-sm">
              <Flame className="h-4 w-4 shrink-0 text-orange-500" />
              <span>Isıtma</span>
            </div>
          </div>

          <div className="mt-auto border-t border-gray-100 pt-4">
            <div className="flex items-center justify-between gap-2">
              <PriceDisplay
                model={product.model}
                brand={brand}
                className={`text-base font-bold sm:text-lg ${theme.price}`}
              />
              <span className={`shrink-0 text-sm font-medium md:group-hover:translate-x-1 md:transition-transform ${theme.inspect}`}>
                İncele →
              </span>
            </div>
          </div>
        </div>
      </div>
    </Link>
  )
}

export function PromoBanner({
  accent,
  title,
  description,
  href,
  buttonLabel,
}: {
  accent: ProductAccent
  title: string
  description: string
  href: string
  buttonLabel: string
}) {
  const theme = ACCENT_THEME[accent]

  return (
    <div className={`mb-5 rounded-2xl p-5 text-white shadow-lg sm:mb-6 sm:p-6 md:p-8 ${theme.banner}`}>
      <div className="flex flex-col items-start justify-between gap-4 md:flex-row md:items-center md:gap-6">
        <div className="flex items-start gap-3 sm:items-center sm:gap-4">
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-white/20 sm:h-14 sm:w-14">
            <Calculator className="h-7 w-7 sm:h-8 sm:w-8" />
          </div>
          <div className="min-w-0">
            <h3 className="text-base font-bold sm:text-lg md:text-xl">{title}</h3>
            <p className={`mt-1 text-sm sm:text-base ${theme.bannerSub}`}>{description}</p>
          </div>
        </div>
        <Link
          href={href}
          className={`inline-flex min-h-11 w-full shrink-0 items-center justify-center gap-2 rounded-xl bg-white px-6 py-3 font-semibold transition-colors md:w-auto ${theme.bannerBtn}`}
        >
          {buttonLabel}
          <ArrowLeft className="h-4 w-4 rotate-180" />
        </Link>
      </div>
    </div>
  )
}

export function ProductCategorySection({
  title,
  desc,
  products,
  brand,
  accent,
}: {
  title: string
  desc: string
  products: ListingProduct[]
  brand: string
  accent: ProductAccent
}) {
  if (products.length === 0) return null

  return (
    <section className="mb-8 sm:mb-12">
      <div className="mb-4 sm:mb-6">
        <h2 className="text-xl font-bold text-gray-900 sm:text-2xl">{title}</h2>
        <p className="text-sm text-gray-500 sm:text-base">{desc}</p>
      </div>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 sm:gap-6 xl:grid-cols-3">
        {products.map((product) => (
          <ProductCard key={product.id} product={product} brand={brand} accent={accent} />
        ))}
      </div>
    </section>
  )
}

export function EmptyFilterResults() {
  return (
    <div className="py-10 text-center sm:py-12">
      <p className="text-base text-gray-500 sm:text-lg">Filtrelere uygun ürün bulunamadı.</p>
      <button
        onClick={() => window.location.reload()}
        className="mt-4 min-h-11 text-blue-600 active:underline md:hover:underline"
      >
        Filtreleri temizle
      </button>
    </div>
  )
}

export function ContactCtaSection({
  accent,
  description,
}: {
  accent: ProductAccent
  description?: string
}) {
  const theme = ACCENT_THEME[accent]
  const defaultDesc =
    'Uzman ekibimiz ihtiyaçlarınızı analiz ederek en uygun klima çözümünü sunmaktadır. Hemen iletişime geçin, size en yakın bayimizle birlikte en doğru seçimi yapalım.'

  return (
    <div className="mt-10 rounded-2xl border border-gray-100 bg-white p-5 shadow-sm sm:mt-16 sm:p-8 md:p-12">
      <div className="grid items-center gap-6 md:grid-cols-2 md:gap-8">
        <div>
          <h3 className="mb-3 text-xl font-bold text-gray-900 sm:mb-4 sm:text-2xl">
            Size Özel Teklif İster misiniz?
          </h3>
          <p className="mb-5 text-sm text-gray-600 sm:mb-6 sm:text-base">
            {description ?? defaultDesc}
          </p>
          <Link
            href="/iletisim"
            className={`inline-flex min-h-11 w-full items-center justify-center gap-2 rounded-xl px-6 py-3 font-semibold text-white transition-colors sm:w-auto ${theme.ctaBtn}`}
          >
            İletişime Geç
            <ArrowLeft className="h-4 w-4 rotate-180" />
          </Link>
        </div>
        <div className="grid grid-cols-2 gap-3 sm:gap-4">
          <div className="rounded-xl bg-gray-50 p-3 text-center sm:p-4">
            <Wind className="mx-auto mb-2 h-7 w-7 text-blue-500 sm:h-8 sm:w-8" />
            <p className="text-xs text-gray-600 sm:text-sm">Profesyonel Montaj</p>
          </div>
          <div className="rounded-xl bg-gray-50 p-3 text-center sm:p-4">
            <Shield className="mx-auto mb-2 h-7 w-7 text-green-500 sm:h-8 sm:w-8" />
            <p className="text-xs text-gray-600 sm:text-sm">Garanti Destek</p>
          </div>
          <div className="rounded-xl bg-gray-50 p-3 text-center sm:p-4">
            <Clock className="mx-auto mb-2 h-7 w-7 text-purple-500 sm:h-8 sm:w-8" />
            <p className="text-xs text-gray-600 sm:text-sm">7/24 Servis</p>
          </div>
          <div className="rounded-xl bg-gray-50 p-3 text-center sm:p-4">
            <Star className="mx-auto mb-2 h-7 w-7 text-yellow-500 sm:h-8 sm:w-8" />
            <p className="text-xs text-gray-600 sm:text-sm">Kalite Belgeli</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export function ProductListingLayout({
  allProducts,
  filteredProducts,
  onFilterChange,
  brand,
  accent,
  banner,
  ctaDescription,
  children,
}: {
  allProducts: ListingProduct[]
  filteredProducts: ListingProduct[]
  onFilterChange: (products: ListingProduct[]) => void
  brand: string
  accent: ProductAccent
  banner: React.ReactNode
  ctaDescription?: string
  children: React.ReactNode
}) {
  return (
    <div className="container mx-auto px-4 pt-4 pb-8 sm:px-6 sm:pt-5 sm:pb-12 md:px-8 md:pt-8 md:pb-14 lg:px-6 lg:pt-6 lg:pb-16">
      {brand.endsWith('_multi') && <MultiPriceNotice className="mb-6 sm:mb-8" />}

      <div className="flex flex-col gap-8 lg:grid lg:grid-cols-[minmax(16rem,17rem)_minmax(0,1fr)] lg:items-start lg:gap-8 xl:gap-10">
        <FilterSidebar products={allProducts} onFilterChange={onFilterChange} brand={brand} />

        <div className="min-w-0">
          <div className="space-y-8 sm:space-y-10 md:space-y-12">
            {banner}
            {children}
          </div>
          {filteredProducts.length === 0 && <EmptyFilterResults />}
        </div>
      </div>

      <ContactCtaSection accent={accent} description={ctaDescription} />
    </div>
  )
}
