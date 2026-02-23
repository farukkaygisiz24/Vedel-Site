import Image from 'next/image'
import Link from 'next/link'
import { notFound } from 'next/navigation'
import { ArrowLeft, Snowflake, Flame, Zap, Download } from 'lucide-react'
import PriceDisplay from '@/components/ui/PriceDisplay'
import productsData from '@/data/products.json'
import { Metadata } from 'next'

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const products = productsData as any

interface Product {
  id: string
  model: string
  name: string
  btu: number
  coolingCapacity: string
  heatingCapacity: string
  energyClass: string
  seer: number
  scop: string
  powerCooling: string
  powerHeating: string
  dimensionsIndoor: string
  dimensionsOutdoor: string
  weightIndoor: string
  weightOutdoor: string
  soundIndoor: string
  soundOutdoor: string
  maxPipeLength: string
  pipeDiameter: string
  catalogUrl: string
  image: string
  features?: string[]
}

function getProductByModel(brand: string, model: string): Product | null {
  const brandData = products[brand]
  if (!brandData) return null

  if (brand === 'mhi' && brandData.split) {
    const series = ['trend', 'plus', 'premium', 'diamond'] as const
    for (const s of series) {
      const products = brandData.split[s]
      if (Array.isArray(products)) {
        const found = products.find(p => p.model.toUpperCase().replace(/-/g, '') === model.toUpperCase().replace(/-/g, ''))
        if (found) return found
      }
    }
  }

  if (brand === 'euroform' && brandData.split) {
    const found = brandData.split.find((p: Product) => p.model.toUpperCase().replace(/-/g, '').replace('SET', '') === model.toUpperCase().replace(/-/g, '').replace('SET', ''))
    if (found) return found
  }

  return null
}

export async function generateStaticParams() {
  const params: { brand: string; model: string }[] = []
  
  if (products.mhi?.split) {
    const series = ['trend', 'plus', 'premium', 'diamond'] as const
    for (const s of series) {
      const prods = products.mhi.split[s]
      if (Array.isArray(prods)) {
        for (const p of prods) {
          params.push({ brand: 'mhi', model: p.model })
        }
      }
    }
  }

  if (products.euroform?.split) {
    for (const p of products.euroform.split) {
      params.push({ brand: 'euroform', model: p.model.replace('-SET', '') })
    }
  }

  return params
}

export async function generateMetadata({ params }: { params: Promise<{ brand: string; model: string }> }): Promise<Metadata> {
  const { brand, model } = await params
  const product = getProductByModel(brand, model)
  
  const brandName = brand === 'mhi' ? 'Mitsubishi Heavy Industries' : 'Euroform'
  const title = product ? `${product.name} | ${brandName}` : 'Ürün Detay'
  const desc = product ? `${product.btu} BTU - ${product.energyClass} enerji sınıfı - ${brandName} klima` : 'Klima ürün detayları'
  
  return {
    title: title + ' | VEDEL Klima',
    description: desc,
    keywords: ['klima', brand, product?.model || model, 'split', `${product?.btu} btu`],
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

export default async function ProductDetailPage({ params }: { params: Promise<{ brand: string; model: string }> }) {
  const { brand, model } = await params
  const product = getProductByModel(brand, model)

  if (!product) {
    notFound()
  }

  const brandData = products[brand]

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="relative bg-gradient-to-r from-red-700 to-red-600 py-12 md:py-16">
        <div className="container mx-auto px-4">
          <Link 
            href={brand === 'mhi' ? '/urunler/splitsistemler/mhi' : '/urunler/splitsistemler/euroform'}
            className="inline-flex items-center gap-2 text-white/80 hover:text-white mb-6 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Ürünlere Dön
          </Link>
          
          <div className="flex flex-col md:flex-row gap-8 items-start">
            <div className="relative w-full md:w-1/2 h-64 md:h-80 bg-white rounded-2xl p-8 shadow-lg">
              <Image
                src={product.image}
                alt={product.model}
                fill
                className="object-contain"
              />
            </div>
            
            <div className="w-full md:w-1/2 text-white">
              <div className="flex items-center gap-3 mb-2">
                <span className="px-3 py-1 bg-white/20 rounded-full text-sm font-medium">
                  {brand === 'mhi' ? 'Mitsubishi Heavy Industries' : 'Euroform'}
                </span>
                <span className="px-3 py-1 bg-red-500 rounded-full text-sm font-bold">
                  {product.btu} BTU
                </span>
              </div>
              
              <h1 className="text-3xl md:text-4xl font-bold mb-2">{product.model}</h1>
              <p className="text-xl text-red-100 mb-4">{product.name}</p>
              
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="flex items-center gap-2">
                  <Snowflake className="w-5 h-5 text-blue-300" />
                  <span>Soğutma: {product.coolingCapacity}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Flame className="w-5 h-5 text-orange-300" />
                  <span>Isıtma: {product.heatingCapacity}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Zap className="w-5 h-5 text-yellow-300" />
                  <span>Enerji: {product.energyClass}</span>
                </div>
              </div>

              <div className="flex flex-wrap gap-4">
                <div className="bg-white rounded-xl p-4 min-w-[180px]">
                  <p className="text-sm text-gray-500 mb-1">Fiyat</p>
                  <PriceDisplay 
                    model={product.model} 
                    className="text-2xl font-bold text-red-600" 
                  />
                </div>
                
                {product.catalogUrl && (
                  <a 
                    href={product.catalogUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 px-6 py-4 bg-white text-red-600 font-semibold rounded-xl hover:bg-gray-100 transition-colors"
                  >
                    <Download className="w-5 h-5" />
                    Katalog İndir
                  </a>
                )}
                
                <Link
                  href="/iletisim"
                  className="flex items-center gap-2 px-6 py-4 bg-red-500 text-white font-semibold rounded-xl hover:bg-red-700 transition-colors"
                >
                  Teklif Al
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-12">
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="p-6 md:p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Teknik Özellikler</h2>
            
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Özellik</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">İç Ünite</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Dış Ünite</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b border-gray-100">
                    <td className="py-3 px-4 text-gray-600">Boyutlar (Y x G x D)</td>
                    <td className="py-3 px-4">{product.dimensionsIndoor}</td>
                    <td className="py-3 px-4">{product.dimensionsOutdoor}</td>
                  </tr>
                  <tr className="border-b border-gray-100">
                    <td className="py-3 px-4 text-gray-600">Net Ağırlık</td>
                    <td className="py-3 px-4">{product.weightIndoor}</td>
                    <td className="py-3 px-4">{product.weightOutdoor}</td>
                  </tr>
                  <tr className="border-b border-gray-100">
                    <td className="py-3 px-4 text-gray-600">Ses Basınç Seviyesi</td>
                    <td className="py-3 px-4">{product.soundIndoor}</td>
                    <td className="py-3 px-4">{product.soundOutdoor}</td>
                  </tr>
                  <tr className="border-b border-gray-100">
                    <td className="py-3 px-4 text-gray-600">SEER (Soğutma)</td>
                    <td className="py-3 px-4" colSpan={2}>{product.seer}</td>
                  </tr>
                  <tr className="border-b border-gray-100">
                    <td className="py-3 px-4 text-gray-600">SCOP (Isıtma)</td>
                    <td className="py-3 px-4" colSpan={2}>{product.scop}</td>
                  </tr>
                  <tr className="border-b border-gray-100">
                    <td className="py-3 px-4 text-gray-600">Güç Tüketimi (Soğutma)</td>
                    <td className="py-3 px-4" colSpan={2}>{product.powerCooling}</td>
                  </tr>
                  <tr className="border-b border-gray-100">
                    <td className="py-3 px-4 text-gray-600">Güç Tüketimi (Isıtma)</td>
                    <td className="py-3 px-4" colSpan={2}>{product.powerHeating}</td>
                  </tr>
                  <tr className="border-b border-gray-100">
                    <td className="py-3 px-4 text-gray-600">Maks. Boru Uzunluğu</td>
                    <td className="py-3 px-4" colSpan={2}>{product.maxPipeLength}</td>
                  </tr>
                  <tr>
                    <td className="py-3 px-4 text-gray-600">Soğutucu Boru Çapı</td>
                    <td className="py-3 px-4" colSpan={2}>{product.pipeDiameter}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div className="mt-12 bg-white rounded-2xl p-8 shadow-sm border border-gray-100">
          <h3 className="text-xl font-bold text-gray-900 mb-4">Teklif Alın</h3>
          <p className="text-gray-600 mb-6">
            Bu ürün hakkında detaylı bilgi almak ve size özel teklif sunulması için bizimle iletişime geçebilirsiniz.
          </p>
          <Link
            href="/iletisim"
            className="inline-flex items-center gap-2 px-6 py-3 bg-red-600 text-white font-semibold rounded-xl hover:bg-red-700 transition-colors"
          >
            İletişime Geç
            <ArrowLeft className="w-4 h-4 rotate-180" />
          </Link>
        </div>
      </div>
    </main>
  )
}
