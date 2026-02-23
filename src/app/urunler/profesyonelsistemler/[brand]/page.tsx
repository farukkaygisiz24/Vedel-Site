import Image from 'next/image'
import Link from 'next/link'
import { notFound } from 'next/navigation'
import { ArrowLeft } from 'lucide-react'
import MhiProfesyonel from '@/components/MhiProfesyonel'
import EuroformProfesyonel from '@/components/EuroformProfesyonel'
import productsData from '@/data/products.json'
import { Metadata } from 'next'

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const products = productsData as any

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

  if (brandKey === 'mhi') {
    if (!products.mhi_profesyonel) notFound()
    const data = products.mhi_profesyonel

    return (
      <main className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
        <div className="relative bg-gradient-to-r from-purple-700 to-purple-600 py-16 md:py-24">
          <div className="absolute inset-0 bg-black/20"></div>
          <div className="absolute inset-0 opacity-10">
            <div className="absolute top-10 left-10 w-32 h-32 border border-white rounded-full"></div>
            <div className="absolute bottom-10 right-10 w-48 h-48 border border-white rounded-full"></div>
            <div className="absolute top-1/2 left-1/3 w-24 h-24 border border-white rounded-full"></div>
          </div>

          <div className="container mx-auto px-4 relative z-10">
            <Link
              href="/"
              className="inline-flex items-center gap-2 text-white/80 hover:text-white mb-6 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              Ana Sayfa
            </Link>

            <div className="flex items-center gap-6 mb-6">
              <div className="relative w-32 h-16 md:w-40 md:h-20 bg-white rounded-xl p-3 shadow-lg">
                <Image
                  src={data.logo}
                  alt={data.brand}
                  fill
                  className="object-contain"
                />
              </div>
              <div>
                <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold text-white">
                  Profesyonel Sistemler
                </h1>
                <p className="text-purple-100 text-lg mt-1">{data.brand}</p>
              </div>
            </div>

            <p className="text-white/90 max-w-2xl text-lg">
              {data.description}
            </p>
          </div>
        </div>

        <MhiProfesyonel data={data} />
      </main>
    )
  }

  if (brandKey === 'euroform') {
    if (!products.euroform_profesyonel) notFound()
    const data = products.euroform_profesyonel

    return (
      <main className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
        <div className="relative bg-gradient-to-r from-teal-700 to-teal-600 py-16 md:py-24">
          <div className="absolute inset-0 bg-black/20"></div>
          <div className="absolute inset-0 opacity-10">
            <div className="absolute top-10 left-10 w-32 h-32 border border-white rounded-full"></div>
            <div className="absolute bottom-10 right-10 w-48 h-48 border border-white rounded-full"></div>
            <div className="absolute top-1/2 left-1/3 w-24 h-24 border border-white rounded-full"></div>
          </div>

          <div className="container mx-auto px-4 relative z-10">
            <Link
              href="/"
              className="inline-flex items-center gap-2 text-white/80 hover:text-white mb-6 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              Ana Sayfa
            </Link>

            <div className="flex items-center gap-6 mb-6">
              <div className="relative w-32 h-16 md:w-40 md:h-20 bg-white rounded-xl p-3 shadow-lg">
                <Image
                  src={data.logo}
                  alt={data.brand}
                  fill
                  className="object-contain"
                />
              </div>
              <div>
                <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold text-white">
                  Profesyonel Sistemler
                </h1>
                <p className="text-teal-100 text-lg mt-1">{data.brand}</p>
              </div>
            </div>

            <p className="text-white/90 max-w-2xl text-lg">
              {data.description}
            </p>
          </div>
        </div>

        <EuroformProfesyonel data={data} />
      </main>
    )
  }

  notFound()
}
