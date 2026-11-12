import { Building2, Settings, Store } from 'lucide-react'

export type HeroCatalogSeries = {
  id: string
  name: string
  brand: string
  tagline: string
  image: string
  imageAlt: string
  href: string
  features: [string, string, string]
}

/** Ana sayfa showroom hero — duvar tipi split serileri */
export const heroCatalogSeries: HeroCatalogSeries[] = [
  {
    id: 'trend',
    name: 'Trend Serisi',
    brand: 'Mitsubishi Heavy Industries',
    tagline: 'Ekonomik giriş, günlük konfor',
    image: '/hero-catalog/trend-show.png',
    imageAlt: 'MHI Trend Serisi duvar tipi klima',
    href: '/urunler/splitsistemler/mhi',
    features: ['A++ enerji sınıfı', 'Ekonomik giriş modeli', 'Sessiz gece modu'],
  },
  {
    id: 'plus',
    name: 'Plus Serisi',
    brand: 'Mitsubishi Heavy Industries',
    tagline: 'Konfor ve enerji tasarrufu',
    image: '/hero-catalog/plus-show.png',
    imageAlt: 'MHI Plus Serisi duvar tipi klima',
    href: '/urunler/splitsistemler/mhi',
    features: ['A+++ enerji sınıfı', 'Konfor ve tasarruf', 'Güçlü ısıtma'],
  },
  {
    id: 'diamond',
    name: 'Diamond Serisi',
    brand: 'Mitsubishi Heavy Industries',
    tagline: 'Premium performans',
    image: '/hero-catalog/diamond-show.png',
    imageAlt: 'MHI Diamond Serisi duvar tipi klima',
    href: '/urunler/splitsistemler/mhi',
    features: ['A+++ premium', 'Düşük ses seviyesi', 'Yüksek SEER'],
  },
  {
    id: 'euroform',
    name: 'Euroform',
    brand: 'Duvar tipi split',
    tagline: 'Güçlü fiyat/performans',
    image: '/hero-catalog/wing-show.png',
    imageAlt: 'Euroform duvar tipi split klima',
    href: '/urunler/splitsistemler/euroform',
    features: ['A++ enerji sınıfı', 'Ekonomik seçim', 'Fiyat / performans'],
  },
]

export const brandCategories = [
  {
    name: 'MHI Split Klimalar',
    desc: 'Ev tipi klimalar',
    image: '/MHI/plusbyeni.png',
    href: '/urunler/splitsistemler/mhi',
    logo: '/mhi-logo.png',
  },
  {
    name: 'Euroform Split Klimalar',
    desc: 'Ev tipi klimalar',
    image: '/euroform/euroformsplit.webp',
    href: '/urunler/splitsistemler/euroform',
    logo: '/euroform.png',
  },
]

export const categories = [
  { name: 'Split Sistemler', desc: 'Ev ve ofisler için', icon: Building2, href: '/urunler/splitsistemler', color: 'from-blue-500 to-cyan-500' },
  { name: 'Multi Sistemler', desc: 'Birden fazla oda için', icon: Settings, href: '/urunler/multisistemler', color: 'from-green-500 to-emerald-500' },
  { name: 'Profesyonel', desc: 'Ticari alanlar için', icon: Store, href: '/urunler/profesyonelsistemler', color: 'from-purple-500 to-pink-500' },
  { name: 'VRF Sistemler', desc: 'Büyük tesisler için', icon: Building2, href: '/urunler/vrfsistemler', color: 'from-orange-500 to-red-500' },
]
