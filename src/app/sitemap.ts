import { MetadataRoute } from 'next'
import { getAllProductRouteParams, getProductDetailPath } from '@/lib/productRoutes'

const BASE_URL = 'https://vedel.com.tr'

type SitemapEntry = MetadataRoute.Sitemap[number]

function entry(
  path: string,
  options: Pick<SitemapEntry, 'changeFrequency' | 'priority'>
): SitemapEntry {
  return {
    url: `${BASE_URL}${path}`,
    lastModified: new Date(),
    ...options,
  }
}

export default function sitemap(): MetadataRoute.Sitemap {
  const staticPages: MetadataRoute.Sitemap = [
    entry('/', { changeFrequency: 'weekly', priority: 1 }),
    entry('/hakkimizda', { changeFrequency: 'monthly', priority: 0.8 }),
    entry('/iletisim', { changeFrequency: 'monthly', priority: 0.8 }),
    entry('/gizlilik-politikasi', { changeFrequency: 'yearly', priority: 0.4 }),
    entry('/kvkk', { changeFrequency: 'yearly', priority: 0.4 }),
    entry('/cerez-politikasi', { changeFrequency: 'yearly', priority: 0.4 }),
    entry('/klimani-sec', { changeFrequency: 'monthly', priority: 0.9 }),
    entry('/urunler/splitsistemler', { changeFrequency: 'weekly', priority: 0.9 }),
    entry('/urunler/splitsistemler/mhi', { changeFrequency: 'weekly', priority: 0.9 }),
    entry('/urunler/splitsistemler/euroform', { changeFrequency: 'weekly', priority: 0.9 }),
    entry('/urunler/multisistemler', { changeFrequency: 'weekly', priority: 0.9 }),
    entry('/urunler/multisistemler/mhi', { changeFrequency: 'weekly', priority: 0.9 }),
    entry('/urunler/multisistemler/mhi/hesaplayici', { changeFrequency: 'weekly', priority: 0.8 }),
    entry('/urunler/multisistemler/euroform', { changeFrequency: 'weekly', priority: 0.9 }),
    entry('/urunler/profesyonelsistemler', { changeFrequency: 'weekly', priority: 0.9 }),
    entry('/urunler/profesyonelsistemler/mhi', { changeFrequency: 'weekly', priority: 0.9 }),
    entry('/urunler/profesyonelsistemler/euroform', { changeFrequency: 'weekly', priority: 0.9 }),
    entry('/urunler/vrfsistemler', { changeFrequency: 'weekly', priority: 0.9 }),
  ]

  const seen = new Set(staticPages.map((page) => page.url))

  const productPages: MetadataRoute.Sitemap = getAllProductRouteParams()
    .map(({ brand, model }) => {
      const path = getProductDetailPath({ brand, model })
      const url = `${BASE_URL}${path}`

      if (seen.has(url)) return null
      seen.add(url)

      const isSplitBrand = brand === 'mhi' || brand === 'euroform'

      return entry(path, {
        changeFrequency: 'weekly',
        priority: isSplitBrand ? 0.7 : 0.65,
      })
    })
    .filter((page): page is SitemapEntry => page !== null)

  return [...staticPages, ...productPages]
}
