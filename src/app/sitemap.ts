import { MetadataRoute } from 'next'
import productsData from '@/data/products.json'

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const products = productsData as any

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = 'https://vedel.com.tr'

  const staticPages = [
    { url: baseUrl, lastModified: new Date(), changeFrequency: 'weekly' as const, priority: 1 },
    { url: `${baseUrl}/hakkimizda`, lastModified: new Date(), changeFrequency: 'monthly' as const, priority: 0.8 },
    { url: `${baseUrl}/iletisim`, lastModified: new Date(), changeFrequency: 'monthly' as const, priority: 0.8 },
    { url: `${baseUrl}/klimani-sec`, lastModified: new Date(), changeFrequency: 'monthly' as const, priority: 0.9 },
    { url: `${baseUrl}/urunler/splitsistemler`, lastModified: new Date(), changeFrequency: 'weekly' as const, priority: 0.9 },
    { url: `${baseUrl}/urunler/splitsistemler/mhi`, lastModified: new Date(), changeFrequency: 'weekly' as const, priority: 0.9 },
    { url: `${baseUrl}/urunler/splitsistemler/euroform`, lastModified: new Date(), changeFrequency: 'weekly' as const, priority: 0.9 },
    { url: `${baseUrl}/urunler/multisistemler`, lastModified: new Date(), changeFrequency: 'weekly' as const, priority: 0.9 },
    { url: `${baseUrl}/urunler/multisistemler/mhi`, lastModified: new Date(), changeFrequency: 'weekly' as const, priority: 0.9 },
    { url: `${baseUrl}/urunler/multisistemler/mhi/hesaplayici`, lastModified: new Date(), changeFrequency: 'weekly' as const, priority: 0.8 },
    { url: `${baseUrl}/urunler/multisistemler/euroform`, lastModified: new Date(), changeFrequency: 'weekly' as const, priority: 0.9 },
    { url: `${baseUrl}/urunler/profesyonelsistemler`, lastModified: new Date(), changeFrequency: 'weekly' as const, priority: 0.9 },
    { url: `${baseUrl}/urunler/profesyonelsistemler/mhi`, lastModified: new Date(), changeFrequency: 'weekly' as const, priority: 0.9 },
    { url: `${baseUrl}/urunler/profesyonelsistemler/euroform`, lastModified: new Date(), changeFrequency: 'weekly' as const, priority: 0.9 },
    { url: `${baseUrl}/urunler/vrfsistemler`, lastModified: new Date(), changeFrequency: 'weekly' as const, priority: 0.9 },
  ]

  const productPages: MetadataRoute.Sitemap = []

  if (products.mhi?.split) {
    const series = ['trend', 'plus', 'diamond', 'diamond_titanyum', 'yuksek_kapasite']
    for (const s of series) {
      const prods = products.mhi.split[s]
      if (Array.isArray(prods)) {
        for (const p of prods) {
          productPages.push({
            url: `${baseUrl}/urunler/mhi/${p.model.replace('-SET', '')}`,
            lastModified: new Date(),
            changeFrequency: 'weekly' as const,
            priority: 0.7,
          })
        }
      }
    }
  }

  if (products.euroform?.split) {
    for (const p of products.euroform.split) {
      productPages.push({
        url: `${baseUrl}/urunler/euroform/${p.model.replace('-SET', '')}`,
        lastModified: new Date(),
        changeFrequency: 'weekly' as const,
        priority: 0.7,
      })
    }
  }

  return [...staticPages, ...productPages]
}
