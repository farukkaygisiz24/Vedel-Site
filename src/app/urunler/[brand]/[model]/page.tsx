import { notFound } from 'next/navigation'
import ProductDetailView from '@/components/products/ProductDetailView'
import productsData from '@/data/products.json'
import { getAllProductRouteParams } from '@/lib/productRoutes'
import { Metadata } from 'next'

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const products = productsData as any

// ===================== HELPERS =====================

const BRAND_NAMES: Record<string, string> = {
  mhi: 'Mitsubishi Heavy Industries',
  euroform: 'Euroform',
  mhi_multi: 'Mitsubishi Heavy Industries',
  mhi_profesyonel: 'Mitsubishi Heavy Industries',
  euroform_multi: 'Euroform',
  euroform_profesyonel: 'Euroform',
}

const BACK_LINKS: Record<string, string> = {
  mhi: '/urunler/splitsistemler/mhi',
  euroform: '/urunler/splitsistemler/euroform',
  mhi_multi: '/urunler/multisistemler/mhi',
  mhi_profesyonel: '/urunler/profesyonelsistemler/mhi',
  euroform_multi: '/urunler/multisistemler/euroform',
  euroform_profesyonel: '/urunler/profesyonelsistemler/euroform',
}

function normalizeModel(m: string) {
  return m.toUpperCase().replace(/-/g, '').replace(/SET/g, '')
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function getProductByModel(brand: string, model: string): any | null {
  const brandData = products[brand]
  if (!brandData) return null

  const normalizedModel = normalizeModel(model)

  if (brand === 'mhi' && brandData.split) {
    const series = ['trend', 'plus', 'premium', 'diamond', 'yuksek_kapasite', 'diamond_titanyum'] as const
    for (const s of series) {
      const items = brandData.split[s]
      if (Array.isArray(items)) {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const found = items.find((p: any) => normalizeModel(p.model) === normalizedModel)
        if (found) return found
      }
    }
  }

  if (brand === 'euroform' && brandData.split) {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const found = brandData.split.find((p: any) => normalizeModel(p.model) === normalizedModel)
    if (found) return found
  }

  if (brandData.categories) {
    for (const categoryKey of Object.keys(brandData.categories)) {
      const items = brandData.categories[categoryKey]
      if (Array.isArray(items)) {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const found = items.find((p: any) => normalizeModel(p.model) === normalizedModel)
        if (found) return found
      }
    }
  }

  return null
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function isSplitProduct(product: any): boolean {
  return !!product.dimensionsIndoor
}

// ===================== STATIC PARAMS =====================

export async function generateStaticParams() {
  return getAllProductRouteParams()
}

// ===================== METADATA =====================

export async function generateMetadata({ params }: { params: Promise<{ brand: string; model: string }> }): Promise<Metadata> {
  const { brand, model } = await params
  const product = getProductByModel(brand, model)
  
  const brandName = BRAND_NAMES[brand] || brand
  const title = product ? `${product.name} ${product.model} | ${brandName}` : 'Ürün Detay'
  const desc = product ? `${product.btu} BTU - ${product.energyClass} enerji sınıfı - ${brandName} klima` : 'Klima ürün detayları'
  
  return {
    title,
    description: desc,
    keywords: ['klima', brand, product?.model || model, `${product?.btu} btu`],
    openGraph: {
      type: 'website',
      locale: 'tr_TR',
      url: `https://vedel.com.tr/urunler/${brand}/${model}`,
      siteName: 'VEDEL Klima',
      title: title + ' | VEDEL Klima',
      description: desc,
      images: product?.image ? [{ url: `/${product.image}`, width: 1200, height: 630, alt: title }] : [{ url: '/vedel-logo.png', width: 1200, height: 630, alt: title }],
    },
    twitter: {
      card: 'summary_large_image',
      title: title + ' | VEDEL Klima',
      description: desc,
      images: product?.image ? [`/${product.image}`] : ['/vedel-logo.png'],
    },
  }
}

// ===================== PAGE =====================

export default async function ProductDetailPage({ params }: { params: Promise<{ brand: string; model: string }> }) {
  const { brand, model } = await params
  const product = getProductByModel(brand, model)

  if (!product) {
    notFound()
  }

  const brandName = BRAND_NAMES[brand] || brand
  const backLink = BACK_LINKS[brand] || '/urunler/splitsistemler'
  const isSplit = isSplitProduct(product)

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <ProductDetailView
        product={product}
        brand={brand}
        brandName={brandName}
        backLink={backLink}
        isSplit={isSplit}
      />
    </main>
  )
}
