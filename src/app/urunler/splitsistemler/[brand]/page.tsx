import { notFound } from 'next/navigation'
import MhiProducts from '@/components/MhiProducts'
import EuroformSplit from '@/components/EuroformSplit'
import BrandProductHero from '@/components/products/BrandProductHero'
import productsData from '@/data/products.json'
import { Metadata } from 'next'

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const products = productsData as any

interface Product {
  id: string
  model: string
  name: string
  btu: number
  energyClass: string
  coolingCapacity: string
  heatingCapacity: string
  image: string
}

interface MhiSplitData {
  brand: string
  logo: string
  description: string
  split: {
    trend: Product[]
    plus: Product[]
    diamond: Product[]
    diamond_titanyum: Product[]
    yuksek_kapasite: Product[]
  }
}

interface EuroformData {
  brand: string
  logo: string
  description: string
  split: Product[]
}

type BrandData = MhiSplitData | EuroformData

const HERO_CONFIG: Record<string, { gradientClass: string; subtitleClass: string }> = {
  mhi: {
    gradientClass: 'bg-gradient-to-r from-red-700 to-red-600',
    subtitleClass: 'text-red-100',
  },
  euroform: {
    gradientClass: 'bg-gradient-to-r from-orange-700 to-orange-600',
    subtitleClass: 'text-orange-100',
  },
}

export function generateStaticParams() {
  return [
    { brand: 'mhi' },
    { brand: 'euroform' }
  ]
}

export async function generateMetadata({ params }: { params: Promise<{ brand: string }> }): Promise<Metadata> {
  const { brand } = await params
  const brandKey = brand.toLowerCase()

  const brandNames: Record<string, { title: string; desc: string }> = {
    mhi: { title: 'MHI Split Klimalar | Mitsubishi Heavy Industries', desc: 'Mitsubishi Heavy Industries split klimalar. Trend, Plus, Diamond serileri. A++ enerji sınıfı.' },
    euroform: { title: 'Euroform Split Klimalar | Wing Serisi', desc: 'Euroform Wing serisi split klimalar. Yüksek enerji verimliliği ve modern tasarım.' }
  }

  const info = brandNames[brandKey] || { title: 'Split Klimalar', desc: 'Split klima modelleri' }

  return {
    title: info.title,
    description: info.desc,
    keywords: ['split klima', brandKey === 'mhi' ? 'mitsubishi heavy' : 'euroform', 'inverter klima'],
    openGraph: {
      type: 'website',
      locale: 'tr_TR',
      url: `https://vedel.com.tr/urunler/splitsistemler/${brand}`,
      siteName: 'VEDEL Klima',
      title: info.title + ' | VEDEL Klima',
      description: info.desc,
      images: [{ url: '/vedel-logo.png', width: 1200, height: 630, alt: info.title }],
    },
    twitter: {
      card: 'summary_large_image',
      title: info.title + ' | VEDEL Klima',
      description: info.desc,
      images: ['/vedel-logo.png'],
    },
  }
}

export default async function SplitSistemlerPage({ params }: { params: Promise<{ brand: string }> }) {
  const { brand } = await params
  const brandKey = brand.toLowerCase()

  if (!products[brandKey]) {
    notFound()
  }

  const data = products[brandKey] as BrandData
  const hero = HERO_CONFIG[brandKey] ?? HERO_CONFIG.mhi

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <BrandProductHero
        gradientClass={hero.gradientClass}
        subtitleClass={hero.subtitleClass}
        pageTitle="Split Sistemler"
        brandName={data.brand}
        logo={data.logo}
        description={data.description}
      />

      {brandKey === 'mhi' ? (
        <MhiProducts data={data as MhiSplitData} />
      ) : (
        <EuroformSplit data={data as EuroformData} />
      )}
    </main>
  )
}
