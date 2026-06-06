import { Building2, Settings, Store } from 'lucide-react'

export const brandCategories = [
  {
    name: 'MHI Split',
    desc: 'Ev tipi klimalar',
    image: '/MHI/plusbyeni.png',
    href: '/urunler/splitsistemler/mhi',
    logo: '/mhi-logo.png',
  },
  {
    name: 'Euroform Split',
    desc: 'Ev tipi klimalar',
    image: '/euroform/euroformsplityeni.png',
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
