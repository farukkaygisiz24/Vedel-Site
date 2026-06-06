'use client'

import { useState, useMemo, useEffect, useRef } from 'react'
import Image from 'next/image'
import Link from 'next/link'
import {
    Home, Building2, Store, Warehouse,
    ArrowLeft, ArrowRight, RotateCcw,
    Snowflake, Sun, Cloud, CloudSun,
    Layers, Building, TreePine,
    Square, RectangleHorizontal, Maximize2,
    ShieldCheck, ShieldX,
    Zap, Monitor, Flame,
    CheckCircle2, Calculator, Phone,
    AlertTriangle, ArrowUpRight
} from 'lucide-react'
import productsData from '@/data/products.json'

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const products = productsData as any

const MIN_BTU = 7000
const MAX_SPLIT_BTU = 30000
const MAX_PROFESYONEL_BTU = 85000

// ===================== TYPES =====================
type MekanTipi = 'ev' | 'ofis' | 'dukkan' | 'depo' | null
type TavanYuksekligi = 2.5 | 3.0 | 3.5
type KatTipi = 'zemin' | 'ara' | 'cati' | null
type GunesDurumu = 'golge' | 'kismi' | 'tam' | null
type PencereBoyutu = 'kucuk' | 'orta' | 'buyuk' | 'cok_buyuk' | null
type ElektronikYogunluk = 'dusuk' | 'orta' | 'yuksek' | null

interface WizardState {
    mekanTipi: MekanTipi
    alan: number
    tavanYuksekligi: TavanYuksekligi
    kat: KatTipi
    gunesDurumu: GunesDurumu
    pencereBoyutu: PencereBoyutu
    izolasyon: boolean
    kisiSayisi: number
    elektronikYogunluk: ElektronikYogunluk
}

// ===================== BTU CALCULATION =====================
function hesaplaBTU(state: WizardState): number {
    const btuPerSqm = 400

    const mekanCarpanlari: Record<string, number> = {
        ev: 1.0, ofis: 1.1, dukkan: 1.15, depo: 1.1
    }
    const katCarpanlari: Record<string, number> = {
        zemin: 1.0, ara: 1.0, cati: 1.1
    }
    const gunesCarpanlari: Record<string, number> = {
        golge: 0.95, kismi: 1.0, tam: 1.15
    }
    const pencereCarpanlari: Record<string, number> = {
        kucuk: 1.0, orta: 1.0, buyuk: 1.1, cok_buyuk: 1.15
    }
    const elektronikEkleme: Record<string, number> = {
        dusuk: 0, orta: 1000, yuksek: 2000
    }

    let btu = state.alan * btuPerSqm

    if (state.tavanYuksekligi >= 3.0) {
        btu *= 1.1
    }

    btu *= mekanCarpanlari[state.mekanTipi || 'ev']
    btu *= katCarpanlari[state.kat || 'ara']
    btu *= gunesCarpanlari[state.gunesDurumu || 'kismi']
    btu *= pencereCarpanlari[state.pencereBoyutu || 'orta']
    btu *= state.izolasyon ? 0.95 : 1.1
    btu += state.kisiSayisi * 400
    btu += elektronikEkleme[state.elektronikYogunluk || 'dusuk']

    return Math.round(Math.max(btu, MIN_BTU))
}

// ===================== MATCHING PRODUCTS =====================
interface MatchedProduct {
    id: string
    model: string
    name: string
    btu: number
    energyClass: string
    coolingCapacity: string
    heatingCapacity: string
    image: string
    brand: string
    type: string
    link: string
}

const DEFAULT_PRODUCT_IMAGES: Record<string, string> = {
    MHI: '/MHI/trend.jpg',
    Euroform: '/euroform/euroformsplit.jpg',
}

function resolveProductImage(image: string | undefined, brand: string): string {
    if (image?.startsWith('/')) return image
    return DEFAULT_PRODUCT_IMAGES[brand] ?? '/MHI/trend.jpg'
}

function getProductDetailLink(brand: string, model: string): string {
    const brandSlug = brand.toLowerCase()
    const modelSlug = model.replace(/-SET$/i, '')
    return `/urunler/${brandSlug}/${modelSlug}`
}

function getMatchingProducts(btu: number): MatchedProduct[] {
    const matched: MatchedProduct[] = []

    // MHI split
    if (products.mhi?.split) {
        const categories = products.mhi.split
        for (const catKey of Object.keys(categories)) {
            const catProducts = categories[catKey]
            if (Array.isArray(catProducts)) {
                for (const p of catProducts) {
                    if (p.btu >= btu * 0.8 && p.btu <= btu * 1.25) {
                        matched.push({
                            ...p,
                            image: resolveProductImage(p.image, 'MHI'),
                            brand: 'MHI',
                            type: 'Split',
                            link: getProductDetailLink('MHI', p.model),
                        })
                    }
                }
            }
        }
    }

    // Euroform split
    if (products.euroform?.split) {
        for (const p of products.euroform.split) {
            if (p.btu >= btu * 0.8 && p.btu <= btu * 1.25) {
                matched.push({
                    ...p,
                    image: resolveProductImage(p.image, 'Euroform'),
                    brand: 'Euroform',
                    type: 'Split',
                    link: getProductDetailLink('Euroform', p.model),
                })
            }
        }
    }

    // Sort by closest BTU match
    matched.sort((a, b) => Math.abs(a.btu - btu) - Math.abs(b.btu - btu))

    return matched.slice(0, 6)
}

// ===================== STEP COMPONENTS =====================

function OptionCard({
    icon, label, description, selected, onClick, color = 'blue'
}: {
    icon: React.ReactNode
    label: string
    description?: string
    selected: boolean
    onClick: () => void
    color?: string
}) {
    const colors: Record<string, { bg: string; border: string; text: string; ring: string }> = {
        blue: { bg: 'bg-blue-50', border: 'border-blue-500', text: 'text-blue-700', ring: 'ring-blue-200' },
        red: { bg: 'bg-red-50', border: 'border-red-500', text: 'text-red-700', ring: 'ring-red-200' },
        green: { bg: 'bg-green-50', border: 'border-green-500', text: 'text-green-700', ring: 'ring-green-200' },
        orange: { bg: 'bg-orange-50', border: 'border-orange-500', text: 'text-orange-700', ring: 'ring-orange-200' },
        purple: { bg: 'bg-purple-50', border: 'border-purple-500', text: 'text-purple-700', ring: 'ring-purple-200' },
    }
    const c = colors[color] || colors.blue

    return (
        <button
            onClick={onClick}
            className={`
        relative w-full min-h-11 p-4 sm:p-5 rounded-2xl border-2 transition-all duration-300 text-left
        ${selected
                    ? `${c.bg} ${c.border} ${c.text} ring-4 ${c.ring} shadow-lg sm:scale-[1.02]`
                    : 'bg-white border-gray-200 active:border-gray-300 md:hover:border-gray-300 md:hover:shadow-md md:hover:scale-[1.01]'
                }
      `}
        >
            {selected && (
                <div className="absolute top-2.5 right-2.5 sm:top-3 sm:right-3">
                    <CheckCircle2 className={`w-5 h-5 ${c.text}`} />
                </div>
            )}
            <div className={`w-10 h-10 sm:w-12 sm:h-12 rounded-xl flex items-center justify-center mb-2 sm:mb-3 ${selected ? c.bg : 'bg-gray-100'}`}>
                <div className={selected ? c.text : 'text-gray-500'}>{icon}</div>
            </div>
            <h4 className={`font-bold text-sm sm:text-base ${selected ? c.text : 'text-gray-900'}`}>{label}</h4>
            {description && (
                <p className={`text-sm mt-1 ${selected ? `${c.text} opacity-80` : 'text-gray-500'}`}>{description}</p>
            )}
        </button>
    )
}

function StepMekanTipi({ state, onChange }: { state: WizardState; onChange: (v: MekanTipi) => void }) {
    const options: { value: MekanTipi; icon: React.ReactNode; label: string; description: string }[] = [
        { value: 'ev', icon: <Home className="w-6 h-6" />, label: 'Ev / Daire', description: 'Yatak odası, salon, mutfak' },
        { value: 'ofis', icon: <Building2 className="w-6 h-6" />, label: 'Ofis', description: 'Çalışma alanı, toplantı odası' },
        { value: 'dukkan', icon: <Store className="w-6 h-6" />, label: 'Dükkan / Mağaza', description: 'Perakende, kafe, restoran' },
        { value: 'depo', icon: <Warehouse className="w-6 h-6" />, label: 'Atölye / Depo', description: 'Üretim alanı, depolama' },
    ]

    return (
        <div className="space-y-3">
            <h2 className="text-xl sm:text-2xl md:text-3xl font-bold text-gray-900 mb-1 sm:mb-2">Mekan Tipini Seçin</h2>
            <p className="text-sm sm:text-base text-gray-500 mb-4 sm:mb-6">Klimayı kullanacağınız mekanın türünü belirleyin.</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                {options.map(opt => (
                    <OptionCard
                        key={opt.value}
                        icon={opt.icon}
                        label={opt.label}
                        description={opt.description}
                        selected={state.mekanTipi === opt.value}
                        onClick={() => onChange(opt.value)}
                        color="blue"
                    />
                ))}
            </div>
        </div>
    )
}

function StepOdaBoyutu({ state, onAlanChange, onTavanChange }: {
    state: WizardState
    onAlanChange: (v: number) => void
    onTavanChange: (v: TavanYuksekligi) => void
}) {
    const tavanOptions: { value: TavanYuksekligi; label: string; desc: string }[] = [
        { value: 2.5, label: '2.5 m', desc: 'Standart' },
        { value: 3.0, label: '3.0 m', desc: 'Yüksek' },
        { value: 3.5, label: '3.5 m+', desc: 'Çok yüksek' },
    ]

    return (
        <div className="space-y-6 sm:space-y-8">
            <div>
                <h2 className="text-xl sm:text-2xl md:text-3xl font-bold text-gray-900 mb-1 sm:mb-2">Oda Boyutu</h2>
                <p className="text-sm sm:text-base text-gray-500 mb-4 sm:mb-6">Odanızın alanını ve tavan yüksekliğini belirtin.</p>
            </div>

            {/* Alan slider */}
            <div>
                <div className="flex items-center justify-between mb-3">
                    <label className="text-sm font-semibold text-gray-700">Oda Alanı</label>
                    <div className="flex items-center gap-2">
                        <input
                            type="number"
                            value={state.alan}
                            onChange={(e) => {
                                const v = parseInt(e.target.value) || 10
                                onAlanChange(Math.max(10, Math.min(200, v)))
                            }}
                            className="w-20 text-right text-lg font-bold text-blue-600 border border-gray-200 rounded-lg px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-300"
                        />
                        <span className="text-gray-500 font-medium">m²</span>
                    </div>
                </div>
                <input
                    type="range"
                    min={10}
                    max={200}
                    value={state.alan}
                    onChange={(e) => onAlanChange(parseInt(e.target.value))}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                />
                <div className="flex justify-between text-xs text-gray-400 mt-1">
                    <span>10 m²</span>
                    <span>50 m²</span>
                    <span>100 m²</span>
                    <span>150 m²</span>
                    <span>200 m²</span>
                </div>
            </div>

            {/* Tavan yüksekliği */}
            <div>
                <label className="text-sm font-semibold text-gray-700 mb-3 block">Tavan Yüksekliği</label>
                <div className="grid grid-cols-3 gap-2 sm:gap-3">
                    {tavanOptions.map(opt => (
                        <button
                            key={opt.value}
                            onClick={() => onTavanChange(opt.value)}
                            className={`
                p-3 sm:p-4 rounded-xl border-2 transition-all duration-200 text-center min-h-11
                ${state.tavanYuksekligi === opt.value
                                    ? 'border-blue-500 bg-blue-50 text-blue-700 ring-4 ring-blue-100'
                                    : 'border-gray-200 active:border-gray-300 md:hover:border-gray-300'
                                }
              `}
                        >
                            <div className="text-base sm:text-xl font-bold">{opt.label}</div>
                            <div className="text-xs text-gray-500 mt-1">{opt.desc}</div>
                        </button>
                    ))}
                </div>
            </div>
        </div>
    )
}

function StepKatGunesYon({ state, onKatChange, onGunesChange }: {
    state: WizardState
    onKatChange: (v: KatTipi) => void
    onGunesChange: (v: GunesDurumu) => void
}) {
    return (
        <div className="space-y-6 sm:space-y-8">
            <div>
                <h2 className="text-xl sm:text-2xl md:text-3xl font-bold text-gray-900 mb-1 sm:mb-2">Kat & Güneş Durumu</h2>
                <p className="text-sm sm:text-base text-gray-500 mb-4 sm:mb-6">Mekanınızın konumunu ve güneş alma durumunu belirtin.</p>
            </div>

            <div>
                <label className="text-sm font-semibold text-gray-700 mb-3 block">Bulunduğunuz Kat</label>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                    <OptionCard
                        icon={<TreePine className="w-6 h-6" />}
                        label="Zemin Kat"
                        description="Giriş seviyesi"
                        selected={state.kat === 'zemin'}
                        onClick={() => onKatChange('zemin')}
                        color="green"
                    />
                    <OptionCard
                        icon={<Layers className="w-6 h-6" />}
                        label="Ara Kat"
                        description="Orta katlar"
                        selected={state.kat === 'ara'}
                        onClick={() => onKatChange('ara')}
                        color="blue"
                    />
                    <OptionCard
                        icon={<Building className="w-6 h-6" />}
                        label="Çatı Katı"
                        description="En üst kat"
                        selected={state.kat === 'cati'}
                        onClick={() => onKatChange('cati')}
                        color="orange"
                    />
                </div>
            </div>

            <div>
                <label className="text-sm font-semibold text-gray-700 mb-3 block">Güneş Alma Durumu</label>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                    <OptionCard
                        icon={<Cloud className="w-6 h-6" />}
                        label="Gölgede"
                        description="Güneş almıyor"
                        selected={state.gunesDurumu === 'golge'}
                        onClick={() => onGunesChange('golge')}
                        color="blue"
                    />
                    <OptionCard
                        icon={<CloudSun className="w-6 h-6" />}
                        label="Kısmi Güneş"
                        description="Günün bir kısmı"
                        selected={state.gunesDurumu === 'kismi'}
                        onClick={() => onGunesChange('kismi')}
                        color="orange"
                    />
                    <OptionCard
                        icon={<Sun className="w-6 h-6" />}
                        label="Tam Güneş"
                        description="Gün boyu güneşli"
                        selected={state.gunesDurumu === 'tam'}
                        onClick={() => onGunesChange('tam')}
                        color="red"
                    />
                </div>
            </div>
        </div>
    )
}

function StepPencereIzolasyon({ state, onPencereChange, onIzolasyonChange }: {
    state: WizardState
    onPencereChange: (v: PencereBoyutu) => void
    onIzolasyonChange: (v: boolean) => void
}) {
    return (
        <div className="space-y-6 sm:space-y-8">
            <div>
                <h2 className="text-xl sm:text-2xl md:text-3xl font-bold text-gray-900 mb-1 sm:mb-2">Pencere & İzolasyon</h2>
                <p className="text-sm sm:text-base text-gray-500 mb-4 sm:mb-6">Odanızdaki pencere boyutu ve yapı izolasyonunu belirtin.</p>
            </div>

            <div>
                <label className="text-sm font-semibold text-gray-700 mb-3 block">Pencere Boyutu</label>
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-2 sm:gap-3">
                    {([
                        { value: 'kucuk' as PencereBoyutu, icon: <Square className="w-5 h-5" />, label: 'Küçük', desc: '< 1 m²' },
                        { value: 'orta' as PencereBoyutu, icon: <RectangleHorizontal className="w-5 h-5" />, label: 'Orta', desc: '1-2 m²' },
                        { value: 'buyuk' as PencereBoyutu, icon: <Maximize2 className="w-5 h-5" />, label: 'Büyük', desc: '2-4 m²' },
                        { value: 'cok_buyuk' as PencereBoyutu, icon: <Maximize2 className="w-6 h-6" />, label: 'Çok Büyük', desc: '> 4 m²' },
                    ]).map(opt => (
                        <OptionCard
                            key={opt.value}
                            icon={opt.icon}
                            label={opt.label}
                            description={opt.desc}
                            selected={state.pencereBoyutu === opt.value}
                            onClick={() => onPencereChange(opt.value)}
                            color="purple"
                        />
                    ))}
                </div>
            </div>

            <div>
                <label className="text-sm font-semibold text-gray-700 mb-3 block">Yapı İzolasyonu</label>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                    <button
                        onClick={() => onIzolasyonChange(true)}
                        className={`
              flex items-center gap-3 sm:gap-4 p-4 sm:p-5 rounded-2xl border-2 transition-all duration-300 min-h-11
              ${state.izolasyon
                                ? 'border-green-500 bg-green-50 ring-4 ring-green-100'
                                : 'border-gray-200 active:border-gray-300 md:hover:border-gray-300'
                            }
            `}
                    >
                        <ShieldCheck className={`w-7 h-7 sm:w-8 sm:h-8 shrink-0 ${state.izolasyon ? 'text-green-600' : 'text-gray-400'}`} />
                        <div className="text-left">
                            <div className={`font-bold ${state.izolasyon ? 'text-green-700' : 'text-gray-900'}`}>İzolasyon Var</div>
                            <div className="text-sm text-gray-500">Dış cephe izoleli</div>
                        </div>
                    </button>
                    <button
                        onClick={() => onIzolasyonChange(false)}
                        className={`
              flex items-center gap-3 sm:gap-4 p-4 sm:p-5 rounded-2xl border-2 transition-all duration-300 min-h-11
              ${!state.izolasyon
                                ? 'border-red-500 bg-red-50 ring-4 ring-red-100'
                                : 'border-gray-200 active:border-gray-300 md:hover:border-gray-300'
                            }
            `}
                    >
                        <ShieldX className={`w-7 h-7 sm:w-8 sm:h-8 shrink-0 ${!state.izolasyon ? 'text-red-600' : 'text-gray-400'}`} />
                        <div className="text-left">
                            <div className={`font-bold ${!state.izolasyon ? 'text-red-700' : 'text-gray-900'}`}>İzolasyon Yok</div>
                            <div className="text-sm text-gray-500">İzolasyonsuz bina</div>
                        </div>
                    </button>
                </div>
            </div>
        </div>
    )
}

function StepKullanim({ state, onKisiChange, onElektronikChange }: {
    state: WizardState
    onKisiChange: (v: number) => void
    onElektronikChange: (v: ElektronikYogunluk) => void
}) {
    return (
        <div className="space-y-6 sm:space-y-8">
            <div>
                <h2 className="text-xl sm:text-2xl md:text-3xl font-bold text-gray-900 mb-1 sm:mb-2">Kullanım Detayları</h2>
                <p className="text-sm sm:text-base text-gray-500 mb-4 sm:mb-6">Son adım! Odadaki kullanım yoğunluğunu belirtin.</p>
            </div>

            <div>
                <div className="flex items-center justify-between mb-3">
                    <label className="text-sm font-semibold text-gray-700">Kişi Sayısı</label>
                    <span className="text-lg font-bold text-blue-600">{state.kisiSayisi} kişi</span>
                </div>
                <div className="flex items-center gap-2 sm:gap-4">
                    <button
                        onClick={() => onKisiChange(Math.max(1, state.kisiSayisi - 1))}
                        className="w-11 h-11 sm:w-12 sm:h-12 shrink-0 rounded-xl border-2 border-gray-200 flex items-center justify-center text-2xl font-bold text-gray-500 active:border-blue-500 active:text-blue-600 transition-all"
                    >
                        −
                    </button>
                    <input
                        type="range"
                        min={1}
                        max={20}
                        value={state.kisiSayisi}
                        onChange={(e) => onKisiChange(parseInt(e.target.value))}
                        className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                    />
                    <button
                        onClick={() => onKisiChange(Math.min(20, state.kisiSayisi + 1))}
                        className="w-11 h-11 sm:w-12 sm:h-12 shrink-0 rounded-xl border-2 border-gray-200 flex items-center justify-center text-2xl font-bold text-gray-500 active:border-blue-500 active:text-blue-600 transition-all"
                    >
                        +
                    </button>
                </div>
                <div className="flex justify-between text-[10px] sm:text-xs text-gray-400 mt-1 px-0 sm:px-14">
                    <span>1</span>
                    <span>5</span>
                    <span>10</span>
                    <span>15</span>
                    <span>20</span>
                </div>
            </div>

            <div>
                <label className="text-sm font-semibold text-gray-700 mb-3 block">Elektronik Cihaz Yoğunluğu</label>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                    <OptionCard
                        icon={<Monitor className="w-6 h-6" />}
                        label="Düşük"
                        description="Sadece aydınlatma"
                        selected={state.elektronikYogunluk === 'dusuk'}
                        onClick={() => onElektronikChange('dusuk')}
                        color="green"
                    />
                    <OptionCard
                        icon={<Zap className="w-6 h-6" />}
                        label="Orta"
                        description="TV, bilgisayar vb."
                        selected={state.elektronikYogunluk === 'orta'}
                        onClick={() => onElektronikChange('orta')}
                        color="orange"
                    />
                    <OptionCard
                        icon={<Flame className="w-6 h-6" />}
                        label="Yüksek"
                        description="Mutfak, çok cihaz"
                        selected={state.elektronikYogunluk === 'yuksek'}
                        onClick={() => onElektronikChange('yuksek')}
                        color="red"
                    />
                </div>
            </div>
        </div>
    )
}

function WizardProductImage({ src, alt, brand }: { src: string; alt: string; brand: string }) {
    const [imageSrc, setImageSrc] = useState(src)
    const fallback = DEFAULT_PRODUCT_IMAGES[brand] ?? '/MHI/trend.jpg'

    useEffect(() => {
        setImageSrc(src)
    }, [src])

    return (
        <div className="flex h-40 sm:h-44 w-full items-center justify-center bg-gray-50 p-3 sm:p-4">
            <Image
                src={imageSrc}
                alt={alt}
                width={320}
                height={200}
                sizes="(max-width: 640px) 90vw, (max-width: 1024px) 45vw, 280px"
                quality={90}
                className="h-full w-auto max-w-full object-contain transition-transform duration-300 group-hover:scale-105"
                onError={() => {
                    if (imageSrc !== fallback) setImageSrc(fallback)
                }}
            />
        </div>
    )
}

function StepSonuc({ btu, matchedProducts }: { btu: number; matchedProducts: MatchedProduct[] }) {
    const btuText = btu.toLocaleString('tr-TR')
    const minBtu = Math.round(btu / 1000) * 1000
    const maxBtu = Math.ceil(btu * 1.3 / 1000) * 1000
    const needsProfesyonel = btu > MAX_SPLIT_BTU
    const maxProfBtuText = MAX_PROFESYONEL_BTU.toLocaleString('tr-TR')

    return (
        <div className="space-y-6 sm:space-y-8">
            <div className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 sm:w-20 sm:h-20 rounded-full bg-gradient-to-br from-blue-500 to-blue-700 text-white mb-3 sm:mb-4">
                    <Calculator className="w-8 h-8 sm:w-10 sm:h-10" />
                </div>
                <h2 className="text-xl sm:text-2xl md:text-3xl font-bold text-gray-900 mb-1 sm:mb-2">Sonuç</h2>
                <p className="text-sm sm:text-base text-gray-500">Odanız için ihtiyaç duyduğunuz kapasiteyi hesapladık.</p>
            </div>

            {/* BTU Result Card */}
            <div className="bg-gradient-to-br from-blue-600 to-blue-800 rounded-2xl sm:rounded-3xl p-5 sm:p-8 text-white text-center shadow-xl">
                <p className="text-blue-200 text-xs sm:text-sm font-medium uppercase tracking-wider mb-2">Hesaplanan Kapasite</p>
                <div className="text-3xl sm:text-4xl md:text-6xl font-extrabold mb-2">
                    {btuText}
                </div>
                <p className="text-blue-200 text-base sm:text-lg">BTU/h</p>
                <div className="mt-4 pt-4 border-t border-white/20">
                    <p className="text-sm text-blue-100">
                        Önerilen kapasite aralığı: <span className="font-bold text-white">{minBtu.toLocaleString('tr-TR')} - {maxBtu.toLocaleString('tr-TR')} BTU</span>
                    </p>
                </div>
            </div>

            {/* Sistem Önerileri */}
            {needsProfesyonel ? (
                <div className="bg-orange-50 border-2 border-orange-200 rounded-2xl p-4 sm:p-6">
                    <div className="flex flex-col sm:flex-row items-start gap-3 sm:gap-4">
                        <div className="w-12 h-12 rounded-xl bg-orange-100 flex items-center justify-center flex-shrink-0">
                            <AlertTriangle className="w-6 h-6 text-orange-600" />
                        </div>
                        <div className="flex-1">
                            <h3 className="text-lg font-bold text-orange-800 mb-2">Profesyonel Klima Sistemi Önerilir</h3>
                            <p className="text-orange-700 mb-4">
                                Hesaplanan kapasite (<span className="font-bold">{btuText} BTU</span>)
                                split klima sınırlarını aşıyor.
                            </p>
                            <p className="text-orange-700 mb-4">
                                Bu kapasite için aşağıdaki profesyonel sistemlerden birini öneriyoruz:
                            </p>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-4">
                                <div className="bg-white rounded-xl p-3 border border-orange-200">
                                    <div className="text-xs text-orange-600 font-medium">Split Sistem</div>
                                    <div className="text-sm font-bold text-gray-900">9.000 - 30.000 BTU</div>
                                </div>
                                <div className="bg-white rounded-xl p-3 border border-orange-200">
                                    <div className="text-xs text-orange-600 font-medium">Profesyonel Sistem</div>
                                    <div className="text-sm font-bold text-gray-900">24.000 - {maxProfBtuText} BTU</div>
                                </div>
                            </div>
                            <Link
                                href="/urunler/profesyonelsistemler/mhi"
                                className="inline-flex w-full sm:w-auto items-center justify-center gap-2 px-5 py-3 bg-orange-600 text-white font-semibold rounded-xl active:bg-orange-700 md:hover:bg-orange-700 transition-colors"
                            >
                                Profesyonel Sistemleri İncele
                                <ArrowUpRight className="w-4 h-4" />
                            </Link>
                        </div>
                    </div>
                </div>
            ) : (
                <div className="bg-green-50 border border-green-200 rounded-2xl p-4">
                    <div className="flex items-center gap-3">
                        <CheckCircle2 className="w-5 h-5 text-green-600" />
                        <span className="text-green-800 font-medium">Split Klima İçin Uygun</span>
                    </div>
                </div>
            )}

            {/* Matched Products */}
            {!needsProfesyonel && matchedProducts.length > 0 && (
                <div>
                    <h3 className="text-lg sm:text-xl font-bold text-gray-900 mb-3 sm:mb-4">Size Uygun Klimalar</h3>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
                        {matchedProducts.map(product => (
                            <Link href={product.link} key={product.id} className="block h-full">
                                <div className="group flex h-full flex-col overflow-hidden rounded-2xl border border-gray-200 bg-white transition-all duration-300 md:hover:-translate-y-1 md:hover:shadow-lg">
                                    <div className="relative flex-shrink-0">
                                        <WizardProductImage
                                            src={product.image}
                                            alt={product.model}
                                            brand={product.brand}
                                        />
                                        <span className="absolute top-2 right-2 inline-block rounded-full bg-blue-100 px-2 py-0.5 text-xs font-bold text-blue-700">
                                            {product.brand}
                                        </span>
                                    </div>
                                    <div className="p-4 flex flex-col flex-1">
                                        <div className="flex items-center gap-2 mb-1">
                                            <span className="text-xs font-bold text-gray-400">{product.type}</span>
                                            <span className="inline-block px-2 py-0.5 bg-green-100 text-green-700 text-xs font-bold rounded-full">
                                                {product.energyClass}
                                            </span>
                                        </div>
                                        <h4 className="font-bold text-gray-900 leading-tight">{product.model}</h4>
                                        <p className="text-sm text-gray-500 mt-1 line-clamp-2">{product.name}</p>
                                        <div className="flex items-center gap-3 mt-3 text-sm">
                                            <span className="flex items-center gap-1 text-blue-600">
                                                <Snowflake className="w-3.5 h-3.5" />
                                                {product.coolingCapacity}
                                            </span>
                                        </div>
                                        <div className="mt-auto pt-4 text-right">
                                            <span className="text-sm font-semibold text-blue-600 group-hover:translate-x-1 transition-transform inline-block">
                                                İncele →
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </Link>
                        ))}
                    </div>
                </div>
            )}

            {matchedProducts.length === 0 && !needsProfesyonel && (
                <div className="bg-orange-50 border border-orange-200 rounded-2xl p-6 text-center">
                    <p className="text-orange-800 font-medium">
                        Hesaplanan kapasiteye uygun hazır ürün bulunamadı. Profesyonel çözümler için bizimle iletişime geçin.
                    </p>
                </div>
            )}

            {/* CTA Buttons */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                <Link
                    href="/iletisim"
                    className="flex min-h-12 items-center justify-center gap-2 px-6 py-4 bg-blue-600 text-white font-semibold rounded-2xl active:bg-blue-700 md:hover:bg-blue-700 transition-colors shadow-lg"
                >
                    <Phone className="w-5 h-5" />
                    Keşif Talep Et
                </Link>
                <a
                    href="tel:+902244132316"
                    className="flex min-h-12 items-center justify-center gap-2 px-6 py-4 border-2 border-blue-600 text-blue-600 font-semibold rounded-2xl active:bg-blue-50 md:hover:bg-blue-50 transition-colors"
                >
                    <Phone className="w-5 h-5" />
                    (0224) 413 23 16
                </a>
            </div>
        </div>
    )
}

// ===================== PROGRESS BAR =====================
function ProgressBar({ step, totalSteps }: { step: number; totalSteps: number }) {
    const stepLabels = ['Mekan', 'Boyut', 'Konum', 'Pencere', 'Kullanım', 'Sonuç']
    const isFinalStep = step === totalSteps - 1
    const progressRatio = totalSteps > 1 ? step / (totalSteps - 1) : 0

    return (
        <div className="mb-6 sm:mb-8">
            <p className="mb-3 text-center text-sm font-medium text-blue-600 sm:hidden">
                {stepLabels[step]} · {step + 1}/{totalSteps}
            </p>

            <div className="relative [--dot:0.625rem] sm:[--dot:0.75rem] md:[--dot:1rem]">
                <div
                    className="absolute top-[var(--dot)] left-[var(--dot)] right-[var(--dot)] h-2 -translate-y-1/2 rounded-full bg-gray-200"
                    aria-hidden="true"
                />
                <div
                    className="absolute top-[var(--dot)] left-[var(--dot)] h-2 -translate-y-1/2 rounded-full bg-gradient-to-r from-blue-500 to-blue-600 transition-all duration-500 ease-out"
                    style={{ width: `calc(var(--dot) + (100% - (var(--dot) * 2)) * ${progressRatio})` }}
                    aria-hidden="true"
                />

                <div className="relative flex items-start justify-between">
                    {stepLabels.map((label, i) => {
                        const isComplete = i < step || (isFinalStep && i === step)
                        const isCurrent = i === step && !isFinalStep

                        return (
                            <div key={i} className="flex w-5 sm:w-6 md:w-8 flex-col items-center">
                                <div
                                    className={`
                                        relative z-10 flex h-5 w-5 sm:h-6 sm:w-6 md:h-8 md:w-8 items-center justify-center rounded-full text-[9px] font-bold transition-all duration-300 sm:text-[10px] md:text-xs
                                        ${isComplete
                                            ? 'bg-blue-600 text-white'
                                            : isCurrent
                                                ? 'bg-blue-100 text-blue-700 ring-2 sm:ring-4 ring-blue-200'
                                                : 'bg-gray-100 text-gray-400'
                                        }
                                    `}
                                >
                                    {isComplete ? '✓' : i + 1}
                                </div>
                                <span className={`mt-2 hidden text-center text-xs leading-tight md:block ${isComplete || isCurrent ? 'font-medium text-blue-600' : 'text-gray-400'}`}>
                                    {label}
                                </span>
                            </div>
                        )
                    })}
                </div>
            </div>
        </div>
    )
}

// ===================== MAIN WIZARD =====================
export default function KlimaSecWizard() {
    const [step, setStep] = useState(0)
    const wizardTopRef = useRef<HTMLDivElement>(null)
    const skipInitialScrollRef = useRef(true)
    const [state, setState] = useState<WizardState>({
        mekanTipi: null,
        alan: 25,
        tavanYuksekligi: 2.5,
        kat: null,
        gunesDurumu: null,
        pencereBoyutu: null,
        izolasyon: true,
        kisiSayisi: 2,
        elektronikYogunluk: null,
    })

    const totalSteps = 6

    const canProceed = useMemo(() => {
        switch (step) {
            case 0: return state.mekanTipi !== null
            case 1: return state.alan >= 10
            case 2: return state.kat !== null && state.gunesDurumu !== null
            case 3: return state.pencereBoyutu !== null
            case 4: return state.elektronikYogunluk !== null
            default: return true
        }
    }, [step, state])

    const btu = useMemo(() => hesaplaBTU(state), [state])
    const matchedProducts = useMemo(() => getMatchingProducts(btu), [btu])

    useEffect(() => {
        if (skipInitialScrollRef.current) {
            skipInitialScrollRef.current = false
            return
        }

        const wizardTop = wizardTopRef.current
        if (!wizardTop) return

        const headerOffset = 88
        const top = wizardTop.getBoundingClientRect().top + window.scrollY - headerOffset
        window.scrollTo({ top: Math.max(0, top), behavior: 'smooth' })
    }, [step])

    const nextStep = () => {
        if (canProceed && step < totalSteps - 1) {
            setStep(s => s + 1)
        }
    }

    const prevStep = () => {
        if (step > 0) setStep(s => s - 1)
    }

    const reset = () => {
        setStep(0)
        setState({
            mekanTipi: null,
            alan: 25,
            tavanYuksekligi: 2.5,
            kat: null,
            gunesDurumu: null,
            pencereBoyutu: null,
            izolasyon: true,
            kisiSayisi: 2,
            elektronikYogunluk: null,
        })
    }

    return (
        <main className="min-h-screen bg-white">
            {/* Header */}
            <div className="relative bg-blue-700 py-8 sm:py-12 md:py-16">
                <div className="container relative z-10 mx-auto px-4 sm:px-6">
                    <Link
                        href="/"
                        className="mb-3 inline-flex min-h-11 items-center gap-2 text-sm text-white/80 transition-colors active:text-white sm:mb-4 sm:text-base"
                    >
                        <ArrowLeft className="h-4 w-4" />
                        Ana Sayfa
                    </Link>

                    <div className="mb-2 flex items-center gap-3 sm:mb-3 sm:gap-4">
                        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-white/20 sm:h-14 sm:w-14">
                            <Calculator className="h-7 w-7 text-white sm:h-8 sm:w-8" />
                        </div>
                        <div className="min-w-0">
                            <h1 className="text-2xl font-bold text-white sm:text-3xl md:text-4xl">Klimanı Seç</h1>
                            <p className="text-sm text-blue-200 sm:text-base">Klima kapasite hesaplayıcı</p>
                        </div>
                    </div>

                    <p className="max-w-xl text-sm text-white/80 sm:text-base">
                        Birkaç soruya yanıt vererek odanıza en uygun klimayı bulun. Hesaplama sadece 1 dakika sürer!
                    </p>
                </div>
            </div>

            {/* Content */}
            <div className="container mx-auto px-4 py-6 sm:px-6 sm:py-8 md:py-12">
                <div ref={wizardTopRef} className="mx-auto max-w-2xl scroll-mt-24">
                    <ProgressBar step={step} totalSteps={totalSteps} />

                    {/* Step Content */}
                    <div className="mb-4 rounded-2xl border border-gray-100 bg-white p-4 shadow-sm sm:mb-6 sm:rounded-3xl sm:p-6 md:p-10">
                        {step === 0 && (
                            <StepMekanTipi
                                state={state}
                                onChange={(v) => setState(s => ({ ...s, mekanTipi: v }))}
                            />
                        )}
                        {step === 1 && (
                            <StepOdaBoyutu
                                state={state}
                                onAlanChange={(v) => setState(s => ({ ...s, alan: v }))}
                                onTavanChange={(v) => setState(s => ({ ...s, tavanYuksekligi: v }))}
                            />
                        )}
                        {step === 2 && (
                            <StepKatGunesYon
                                state={state}
                                onKatChange={(v) => setState(s => ({ ...s, kat: v }))}
                                onGunesChange={(v) => setState(s => ({ ...s, gunesDurumu: v }))}
                            />
                        )}
                        {step === 3 && (
                            <StepPencereIzolasyon
                                state={state}
                                onPencereChange={(v) => setState(s => ({ ...s, pencereBoyutu: v }))}
                                onIzolasyonChange={(v) => setState(s => ({ ...s, izolasyon: v }))}
                            />
                        )}
                        {step === 4 && (
                            <StepKullanim
                                state={state}
                                onKisiChange={(v) => setState(s => ({ ...s, kisiSayisi: v }))}
                                onElektronikChange={(v) => setState(s => ({ ...s, elektronikYogunluk: v }))}
                            />
                        )}
                        {step === 5 && (
                            <StepSonuc btu={btu} matchedProducts={matchedProducts} />
                        )}
                    </div>

                    {/* Navigation */}
                    <div className="flex flex-col-reverse gap-3 sm:flex-row sm:items-center sm:justify-between">
                        {step > 0 && step < 5 ? (
                            <button
                                onClick={prevStep}
                                className="inline-flex min-h-12 w-full sm:w-auto items-center justify-center gap-2 rounded-xl px-5 py-3 font-medium text-gray-600 transition-all active:bg-gray-100 sm:justify-start md:hover:bg-gray-100 md:hover:text-gray-900"
                            >
                                <ArrowLeft className="h-4 w-4" />
                                Geri
                            </button>
                        ) : step === 5 ? (
                            <button
                                onClick={reset}
                                className="inline-flex min-h-12 w-full sm:w-auto items-center justify-center gap-2 rounded-xl px-5 py-3 font-medium text-gray-600 transition-all active:bg-gray-100 sm:justify-start md:hover:bg-gray-100 md:hover:text-gray-900"
                            >
                                <RotateCcw className="h-4 w-4" />
                                Yeniden Hesapla
                            </button>
                        ) : (
                            <div className="hidden sm:block" />
                        )}

                        {step < 4 && (
                            <button
                                onClick={nextStep}
                                disabled={!canProceed}
                                className={`
                  inline-flex min-h-12 w-full sm:w-auto items-center justify-center gap-2 rounded-xl px-8 py-3 font-semibold transition-all duration-200 sm:shadow-lg
                  ${canProceed
                                        ? 'bg-blue-600 text-white active:bg-blue-700 md:hover:bg-blue-700 md:hover:shadow-xl'
                                        : 'cursor-not-allowed bg-gray-200 text-gray-400 shadow-none'
                                    }
                `}
                            >
                                Devam
                                <ArrowRight className="h-4 w-4" />
                            </button>
                        )}

                        {step === 4 && (
                            <button
                                onClick={nextStep}
                                disabled={!canProceed}
                                className={`
                  inline-flex min-h-12 w-full sm:w-auto items-center justify-center gap-2 rounded-xl px-8 py-3 font-semibold transition-all duration-200 sm:shadow-lg
                  ${canProceed
                                        ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white active:from-blue-700 active:to-indigo-700 md:hover:from-blue-700 md:hover:to-indigo-700 md:hover:shadow-xl'
                                        : 'cursor-not-allowed bg-gray-200 text-gray-400 shadow-none'
                                    }
                `}
                            >
                                <Calculator className="h-4 w-4" />
                                Hesapla
                            </button>
                        )}
                    </div>
                </div>
            </div>
        </main>
    )
}
