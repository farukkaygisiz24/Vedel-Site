import Image from 'next/image'
import Link from 'next/link'
import { ArrowLeft, Snowflake, Flame, Zap, Download, Wind, Clock, Shield, Star } from 'lucide-react'
import PriceDisplay from '@/components/ui/PriceDisplay'
import {
  getProductAccent,
  getSpecTableStyle,
  formatBtu,
  DETAIL_HERO,
  ACCENT_THEME,
  type ProductAccent,
} from '@/components/products/productTheme'
import MultiPriceNotice from '@/components/products/MultiPriceNotice'

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type ProductDetailData = Record<string, any>

interface SpecRow {
  label: string
  indoor?: string | number
  outdoor?: string | number
  value?: string | number
}

function buildSpecRows(product: ProductDetailData, isSplit: boolean): SpecRow[] {
  const rows: SpecRow[] = [
    {
      label: 'Boyutlar (Y x G x D)',
      indoor: isSplit ? product.dimensionsIndoor : undefined,
      outdoor: isSplit ? product.dimensionsOutdoor : undefined,
      value: isSplit ? undefined : product.dimensions,
    },
    {
      label: 'Net Ağırlık',
      indoor: isSplit ? product.weightIndoor : undefined,
      outdoor: isSplit ? product.weightOutdoor : undefined,
      value: isSplit ? undefined : product.weight,
    },
    {
      label: 'Ses Basınç Seviyesi',
      indoor: isSplit ? product.soundIndoor : undefined,
      outdoor: isSplit ? product.soundOutdoor : undefined,
      value: isSplit ? undefined : product.sound,
    },
    { label: 'SEER (Soğutma)', value: product.seer },
    { label: 'SCOP (Isıtma)', value: product.scop },
  ]

  if (product.powerCooling) {
    rows.push({ label: 'Güç Tüketimi (Soğutma)', value: product.powerCooling })
  }
  if (product.powerHeating) {
    rows.push({ label: 'Güç Tüketimi (Isıtma)', value: product.powerHeating })
  }
  if (product.maxIndoor) {
    rows.push({ label: 'Maks. İç Ünite', value: product.maxIndoor })
  }
  if (product.maxPipeLength) {
    rows.push({ label: 'Maks. Boru Uzunluğu', value: product.maxPipeLength })
  }
  if (product.pipeDiameter) {
    rows.push({ label: 'Soğutucu Boru Çapı', value: product.pipeDiameter })
  }

  return rows
}

function ProductDetailHero({
  product,
  brand,
  brandName,
  backLink,
  accent,
}: {
  product: ProductDetailData
  brand: string
  brandName: string
  backLink: string
  accent: ProductAccent
}) {
  const hero = DETAIL_HERO[accent]
  const theme = ACCENT_THEME[accent]

  return (
    <div className={`relative overflow-hidden ${hero.gradientClass} pt-8 pb-6 sm:pt-10 sm:pb-8 md:pt-12 md:pb-10`}>
      <div className="absolute inset-0 bg-black/20" />
      <div className="pointer-events-none absolute inset-0 opacity-10">
        <div className="absolute left-3 top-4 h-14 w-14 rounded-full border border-white sm:left-8 sm:top-6 sm:h-20 sm:w-20" />
        <div className="absolute bottom-4 right-3 h-20 w-20 rounded-full border border-white sm:bottom-6 sm:right-8 sm:h-28 sm:w-28" />
        <div className="absolute left-1/3 top-1/2 hidden h-16 w-16 rounded-full border border-white md:block" />
      </div>

      <div className="container relative z-10 mx-auto px-4 sm:px-6 md:px-8 lg:px-6">
        <Link
          href={backLink}
          className="mb-4 inline-flex min-h-10 items-center gap-2 text-sm text-white/80 transition-colors active:text-white sm:mb-5"
        >
          <ArrowLeft className="h-4 w-4" />
          Ürünlere Dön
        </Link>

        <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:gap-8 xl:gap-10">
          <div className="flex w-full shrink-0 items-center justify-center rounded-2xl bg-white p-4 shadow-lg sm:p-5 lg:w-[44%] xl:w-[40%]">
            <div className="relative h-40 w-full sm:h-48 md:h-56 lg:h-64 xl:h-72">
              <Image
                src={product.image}
                alt={product.model}
                fill
                className="object-contain"
                sizes="(max-width: 1024px) 90vw, 480px"
                priority
              />
            </div>
          </div>

          <div className="min-w-0 flex-1 text-white">
            <div className="mb-3 flex flex-wrap items-center gap-2">
              <span className="rounded-full bg-white/20 px-3 py-1 text-xs font-medium sm:text-sm">
                {brandName}
              </span>
              <span className={`rounded-full px-3 py-1 text-xs font-bold sm:text-sm ${hero.btuBadge}`}>
                {formatBtu(product.btu)}
              </span>
              <span className="inline-flex items-center gap-1 rounded-full bg-white/20 px-3 py-1 text-xs font-bold sm:text-sm">
                <Zap className="h-3.5 w-3.5" />
                {product.energyClass}
              </span>
            </div>

            <h1 className="text-2xl font-bold sm:text-3xl md:text-4xl">{product.model}</h1>
            <p className={`mt-1 text-base sm:text-lg ${hero.subtitleClass}`}>{product.name}</p>

            <div className="mt-4 grid grid-cols-1 gap-2.5 sm:mt-5 sm:grid-cols-2 sm:gap-3">
              <div className="flex items-center gap-2 rounded-xl bg-white/10 px-3 py-2.5 text-sm sm:text-base">
                <Snowflake className="h-4 w-4 shrink-0 text-blue-200 sm:h-5 sm:w-5" />
                <span className="min-w-0">
                  <span className="block text-xs text-white/70 sm:text-sm">Soğutma</span>
                  {product.coolingCapacity}
                </span>
              </div>
              <div className="flex items-center gap-2 rounded-xl bg-white/10 px-3 py-2.5 text-sm sm:text-base">
                <Flame className="h-4 w-4 shrink-0 text-orange-200 sm:h-5 sm:w-5" />
                <span className="min-w-0">
                  <span className="block text-xs text-white/70 sm:text-sm">Isıtma</span>
                  {product.heatingCapacity}
                </span>
              </div>
              {product.maxIndoor && (
                <div className="flex items-center gap-2 rounded-xl bg-white/10 px-3 py-2.5 text-sm sm:col-span-2 sm:text-base">
                  <span className="text-xs text-white/70 sm:text-sm">Maks. İç Ünite:</span>
                  {product.maxIndoor}
                </div>
              )}
            </div>

            <div className="mt-5 flex flex-col gap-3 sm:mt-6 lg:flex-row lg:items-stretch lg:gap-4">
              <div className="flex flex-col justify-center rounded-xl bg-white p-4 sm:p-5 lg:flex-1">
                <p className="mb-1 text-xs text-gray-500 sm:text-sm">Fiyat</p>
                <PriceDisplay
                  model={product.model}
                  brand={brand}
                  className={`text-xl font-bold sm:text-2xl ${theme.price}`}
                />
              </div>

              {product.catalogUrl && (
                <a
                  href={product.catalogUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={`inline-flex min-h-[72px] w-full items-center justify-center gap-2 rounded-xl bg-white px-5 py-4 text-sm font-semibold transition-colors sm:text-base lg:flex-1 ${hero.catalogBtn}`}
                >
                  <Download className="h-5 w-5 shrink-0" />
                  Katalog İndir
                </a>
              )}

              <Link
                href="/iletisim"
                className={`inline-flex min-h-[72px] w-full items-center justify-center gap-2 rounded-xl px-5 py-4 text-sm font-semibold text-white transition-colors sm:text-base lg:flex-1 ${hero.quoteBtn}`}
              >
                Teklif Al
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function ProductSpecsSection({
  product,
  isSplit,
  accent,
}: {
  product: ProductDetailData
  isSplit: boolean
  accent: ProductAccent
}) {
  const rows = buildSpecRows(product, isSplit)
  const specTableStyle = getSpecTableStyle(accent)

  return (
    <div className="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm">
      <div className="border-b border-gray-200 px-4 py-4 sm:px-6 sm:py-5">
        <h2 className="text-xl font-bold text-gray-900 sm:text-2xl">Teknik Özellikler</h2>
      </div>

      <div className="overflow-x-auto" style={specTableStyle}>
        <table className="product-specs-table">
          <colgroup>
            <col style={{ width: '34%' }} />
            {isSplit ? (
              <>
                <col style={{ width: '33%' }} />
                <col style={{ width: '33%' }} />
              </>
            ) : (
              <col style={{ width: '66%' }} />
            )}
          </colgroup>
          <thead>
            <tr>
              <th>Özellik</th>
              {isSplit ? (
                <>
                  <th>İç Ünite</th>
                  <th>Dış Ünite</th>
                </>
              ) : (
                <th>Değer</th>
              )}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.label}>
                <td>{row.label}</td>
                {isSplit && row.indoor !== undefined ? (
                  <>
                    <td>{row.indoor}</td>
                    <td>{row.outdoor}</td>
                  </>
                ) : (
                  <td colSpan={isSplit ? 2 : 1}>{row.value}</td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function ProductDetailCta({ accent }: { accent: ProductAccent }) {
  const theme = ACCENT_THEME[accent]

  return (
    <div className="mt-8 rounded-2xl border border-gray-100 bg-white p-5 shadow-sm sm:mt-10 sm:p-8 md:p-10">
      <div className="grid items-center gap-6 md:grid-cols-2 md:gap-8">
        <div>
          <h3 className="mb-3 text-xl font-bold text-gray-900 sm:text-2xl">Teklif Alın</h3>
          <p className="mb-5 text-sm text-gray-600 sm:mb-6 sm:text-base">
            Bu ürün hakkında detaylı bilgi almak ve size özel teklif sunulması için bizimle iletişime geçebilirsiniz.
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

export default function ProductDetailView({
  product,
  brand,
  brandName,
  backLink,
  isSplit,
}: {
  product: ProductDetailData
  brand: string
  brandName: string
  backLink: string
  isSplit: boolean
}) {
  const accent = getProductAccent(brand)

  return (
    <>
      <ProductDetailHero
        product={product}
        brand={brand}
        brandName={brandName}
        backLink={backLink}
        accent={accent}
      />

      <div className="container mx-auto px-4 pt-6 pb-8 sm:px-6 sm:pt-8 sm:pb-12 md:px-8 md:pb-14 lg:px-6 lg:pb-16">
        {(brand === 'mhi_multi' || brand === 'euroform_multi') && (
          <MultiPriceNotice className="mb-6 sm:mb-8" />
        )}
        <ProductSpecsSection product={product} isSplit={isSplit} accent={accent} />
        <ProductDetailCta accent={accent} />
      </div>
    </>
  )
}
