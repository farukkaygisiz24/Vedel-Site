import { notFound } from 'next/navigation'
import MhiMulti from '@/components/MhiMulti'
import EuroformMulti from '@/components/EuroformMulti'
import BrandProductHero from '@/components/products/BrandProductHero'
import productsData from '@/data/products.json'
import { Metadata } from 'next'

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const products = productsData as any

const HERO_CONFIG: Record<string, { gradientClass: string; subtitleClass: string; dataKey: string }> = {
  mhi: {
    gradientClass: 'bg-gradient-to-r from-blue-700 to-blue-600',
    subtitleClass: 'text-blue-100',
    dataKey: 'mhi_multi',
  },
  euroform: {
    gradientClass: 'bg-gradient-to-r from-emerald-700 to-emerald-600',
    subtitleClass: 'text-emerald-100',
    dataKey: 'euroform_multi',
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
    mhi: { title: 'MHI Multi Split Klimalar | Tek Dış Ünite', desc: 'Mitsubishi Heavy Industries multi split klimalar. Tek dış üniteye 2-8 iç ünite bağlayın.' },
    euroform: { title: 'Euroform Multi Split Klimalar | Ev ve İşyeri', desc: 'Euroform multi split klimalar. Esnek iç ünite seçenekleri ile ideal çözümler.' }
  }

  const info = brandNames[brandKey] || { title: 'Multi Split Klimalar', desc: 'Multi split klima modelleri' }

  return {
    title: info.title,
    description: info.desc,
    keywords: ['multi klima', 'multi split', brandKey === 'mhi' ? 'mitsubishi heavy' : 'euroform'],
    openGraph: {
      type: 'website',
      locale: 'tr_TR',
      url: `https://vedel.com.tr/urunler/multisistemler/${brand}`,
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

export default async function MultiSistemlerPage({ params }: { params: Promise<{ brand: string }> }) {
  const { brand } = await params
  const brandKey = brand.toLowerCase()
  const config = HERO_CONFIG[brandKey]

  if (!config) notFound()

  const data = products[config.dataKey]
  if (!data) notFound()

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <BrandProductHero
        gradientClass={config.gradientClass}
        subtitleClass={config.subtitleClass}
        pageTitle="Multi Sistemler"
        brandName={data.brand}
        logo={data.logo}
        description={data.description}
      />

      {brandKey === 'mhi' ? (
        <MhiMulti data={data} />
      ) : (
        <EuroformMulti data={data} />
      )}
    </main>
  )
}
