import { notFound } from 'next/navigation'
import MhiProfesyonel from '@/components/MhiProfesyonel'
import EuroformProfesyonel from '@/components/EuroformProfesyonel'
import BrandProductHero from '@/components/products/BrandProductHero'
import productsData from '@/data/products.json'
import { Metadata } from 'next'

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const products = productsData as any

const HERO_CONFIG: Record<string, { gradientClass: string; subtitleClass: string; dataKey: string }> = {
  mhi: {
    gradientClass: 'bg-gradient-to-r from-purple-700 to-purple-600',
    subtitleClass: 'text-purple-100',
    dataKey: 'mhi_profesyonel',
  },
  euroform: {
    gradientClass: 'bg-gradient-to-r from-teal-700 to-teal-600',
    subtitleClass: 'text-teal-100',
    dataKey: 'euroform_profesyonel',
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
    mhi: { title: 'MHI Profesyonel Klimalar | Ticari İklimlendirme', desc: 'Mitsubishi Heavy Industries profesyonel klima sistemleri. Kaset, kanal, tavan tipi üniteler.' },
    euroform: { title: 'Euroform Profesyonel Klimalar | Endüstriyel Çözümler', desc: 'Euroform profesyonel klima sistemleri. Kaset, salon, kanal tipi üniteler.' }
  }
  
  const info = brandNames[brandKey] || { title: 'Profesyonel Klimalar', desc: 'Profesyonel klima modelleri' }
  
  return {
    title: info.title + ' | VEDEL Klima',
    description: info.desc,
    keywords: ['profesyonel klima', 'ticari klima', brandKey === 'mhi' ? 'mitsubishi heavy' : 'euroform'],
    openGraph: {
      type: 'website',
      locale: 'tr_TR',
      url: `https://vedel.com.tr/urunler/profesyonelsistemler/${brand}`,
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

export default async function ProfesyonelSistemlerPage({ params }: { params: Promise<{ brand: string }> }) {
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
        pageTitle="Profesyonel Sistemler"
        brandName={data.brand}
        logo={data.logo}
        description={data.description}
      />

      {brandKey === 'mhi' ? (
        <MhiProfesyonel data={data} />
      ) : (
        <EuroformProfesyonel data={data} />
      )}
    </main>
  )
}
