'use client'

import { useState, useMemo } from 'react'
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
const VRF_THRESHOLD_PERCENT = 130

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
                            brand: 'MHI',
                            type: 'Split',
                            link: `/urunler/splitsistemler/mhi`
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
                    brand: 'Euroform',
                    type: 'Split',
                    link: `/urunler/splitsistemler/euroform`
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
        relative w-full p-5 rounded-2xl border-2 transition-all duration-300 text-left
        ${selected
                    ? `${c.bg} ${c.border} ${c.text} ring-4 ${c.ring} scale-[1.02] shadow-lg`
                    : 'bg-white border-gray-200 hover:border-gray-300 hover:shadow-md hover:scale-[1.01]'
                }
      `}
        >
            {selected && (
                <div className="absolute top-3 right-3">
                    <CheckCircle2 className={`w-5 h-5 ${c.text}`} />
                </div>
            )}
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-3 ${selected ? c.bg : 'bg-gray-100'}`}>
                <div className={selected ? c.text : 'text-gray-500'}>{icon}</div>
            </div>
            <h4 className={`font-bold text-base ${selected ? c.text : 'text-gray-900'}`}>{label}</h4>
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
            <h2 className="text-2xl md:text-3xl font-bold text-gray-900 mb-2">Mekan Tipini Seçin</h2>
            <p className="text-gray-500 mb-6">Klimayı kullanacağınız mekanın türünü belirleyin.</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
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
        <div className="space-y-8">
            <div>
                <h2 className="text-2xl md:text-3xl font-bold text-gray-900 mb-2">Oda Boyutu</h2>
                <p className="text-gray-500 mb-6">Odanızın alanını ve tavan yüksekliğini belirtin.</p>
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
                <div className="grid grid-cols-3 gap-3">
                    {tavanOptions.map(opt => (
                        <button
                            key={opt.value}
                            onClick={() => onTavanChange(opt.value)}
                            className={`
                p-4 rounded-xl border-2 transition-all duration-200 text-center
                ${state.tavanYuksekligi === opt.value
                                    ? 'border-blue-500 bg-blue-50 text-blue-700 ring-4 ring-blue-100'
                                    : 'border-gray-200 hover:border-gray-300'
                                }
              `}
                        >
                            <div className="text-xl font-bold">{opt.label}</div>
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
        <div className="space-y-8">
            <div>
                <h2 className="text-2xl md:text-3xl font-bold text-gray-900 mb-2">Kat & Güneş Durumu</h2>
                <p className="text-gray-500 mb-6">Mekanınızın konumunu ve güneş alma durumunu belirtin.</p>
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
        <div className="space-y-8">
            <div>
                <h2 className="text-2xl md:text-3xl font-bold text-gray-900 mb-2">Pencere & İzolasyon</h2>
                <p className="text-gray-500 mb-6">Odanızdaki pencere boyutu ve yapı izolasyonunu belirtin.</p>
            </div>

            <div>
                <label className="text-sm font-semibold text-gray-700 mb-3 block">Pencere Boyutu</label>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
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
                <div className="grid grid-cols-2 gap-4">
                    <button
                        onClick={() => onIzolasyonChange(true)}
                        className={`
              flex items-center gap-4 p-5 rounded-2xl border-2 transition-all duration-300
              ${state.izolasyon
                                ? 'border-green-500 bg-green-50 ring-4 ring-green-100'
                                : 'border-gray-200 hover:border-gray-300'
                            }
            `}
                    >
                        <ShieldCheck className={`w-8 h-8 ${state.izolasyon ? 'text-green-600' : 'text-gray-400'}`} />
                        <div className="text-left">
                            <div className={`font-bold ${state.izolasyon ? 'text-green-700' : 'text-gray-900'}`}>İzolasyon Var</div>
                            <div className="text-sm text-gray-500">Dış cephe izoleli</div>
                        </div>
                    </button>
                    <button
                        onClick={() => onIzolasyonChange(false)}
                        className={`
              flex items-center gap-4 p-5 rounded-2xl border-2 transition-all duration-300
              ${!state.izolasyon
                                ? 'border-red-500 bg-red-50 ring-4 ring-red-100'
                                : 'border-gray-200 hover:border-gray-300'
                            }
            `}
                    >
                        <ShieldX className={`w-8 h-8 ${!state.izolasyon ? 'text-red-600' : 'text-gray-400'}`} />
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
        <div className="space-y-8">
            <div>
                <h2 className="text-2xl md:text-3xl font-bold text-gray-900 mb-2">Kullanım Detayları</h2>
                <p className="text-gray-500 mb-6">Son adım! Odadaki kullanım yoğunluğunu belirtin.</p>
            </div>

            <div>
                <div className="flex items-center justify-between mb-3">
                    <label className="text-sm font-semibold text-gray-700">Kişi Sayısı</label>
                    <span className="text-lg font-bold text-blue-600">{state.kisiSayisi} kişi</span>
                </div>
                <div className="flex items-center gap-4">
                    <button
                        onClick={() => onKisiChange(Math.max(1, state.kisiSayisi - 1))}
                        className="w-12 h-12 rounded-xl border-2 border-gray-200 flex items-center justify-center text-2xl font-bold text-gray-500 hover:border-blue-500 hover:text-blue-600 transition-all"
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
                        className="w-12 h-12 rounded-xl border-2 border-gray-200 flex items-center justify-center text-2xl font-bold text-gray-500 hover:border-blue-500 hover:text-blue-600 transition-all"
                    >
                        +
                    </button>
                </div>
                <div className="flex justify-between text-xs text-gray-400 mt-1 px-14">
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

function StepSonuc({ btu, matchedProducts }: { btu: number; matchedProducts: MatchedProduct[] }) {
    const btuText = btu.toLocaleString('tr-TR')
    const minBtu = Math.round(btu / 1000) * 1000
    const maxBtu = Math.ceil(btu * 1.3 / 1000) * 1000
    const needsProfesyonel = btu > MAX_SPLIT_BTU
    const maxSplitBtuText = MAX_SPLIT_BTU.toLocaleString('tr-TR')
    const maxProfBtuText = MAX_PROFESYONEL_BTU.toLocaleString('tr-TR')

    return (
        <div className="space-y-8">
            <div className="text-center">
                <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-blue-500 to-blue-700 text-white mb-4">
                    <Calculator className="w-10 h-10" />
                </div>
                <h2 className="text-2xl md:text-3xl font-bold text-gray-900 mb-2">Sonuç</h2>
                <p className="text-gray-500">Odanız için ihtiyaç duyduğunuz kapasiteyi hesapladık.</p>
            </div>

            {/* BTU Result Card */}
            <div className="bg-gradient-to-br from-blue-600 to-blue-800 rounded-3xl p-8 text-white text-center shadow-xl">
                <p className="text-blue-200 text-sm font-medium uppercase tracking-wider mb-2">Hesaplanan Kapasite</p>
                <div className="text-4xl md:text-6xl font-extrabold mb-2">
                    {btuText}
                </div>
                <p className="text-blue-200 text-lg">BTU/h</p>
                <div className="mt-4 pt-4 border-t border-white/20">
                    <p className="text-sm text-blue-100">
                        Önerilen kapasite aralığı: <span className="font-bold text-white">{minBtu.toLocaleString('tr-TR')} - {maxBtu.toLocaleString('tr-TR')} BTU</span>
                    </p>
                </div>
            </div>

            {/* Sistem Önerileri */}
            {needsProfesyonel ? (
                <div className="bg-orange-50 border-2 border-orange-200 rounded-2xl p-6">
                    <div className="flex items-start gap-4">
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
                                className="inline-flex items-center gap-2 px-5 py-3 bg-orange-600 text-white font-semibold rounded-xl hover:bg-orange-700 transition-colors"
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
                    <h3 className="text-xl font-bold text-gray-900 mb-4">Size Uygun Klimalar</h3>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                        {matchedProducts.map(product => (
                            <Link href={product.link} key={product.id}>
                                <div className="group bg-white rounded-2xl border border-gray-200 overflow-hidden hover:shadow-lg hover:-translate-y-1 transition-all duration-300">
                                    <div className="relative h-36 p-3 bg-gray-50">
                                        <Image
                                            src={product.image}
                                            alt={product.model}
                                            fill
                                            className="object-contain group-hover:scale-105 transition-transform"
                                        />
                                        <span className="absolute top-2 right-2 inline-block px-2 py-0.5 bg-blue-100 text-blue-700 text-xs font-bold rounded-full">
                                            {product.brand}
                                        </span>
                                    </div>
                                    <div className="p-4">
                                        <div className="flex items-center gap-2 mb-1">
                                            <span className="text-xs font-bold text-gray-400">{product.type}</span>
                                            <span className="inline-block px-2 py-0.5 bg-green-100 text-green-700 text-xs font-bold rounded-full">
                                                {product.energyClass}
                                            </span>
                                        </div>
                                        <h4 className="font-bold text-gray-900">{product.model}</h4>
                                        <p className="text-sm text-gray-500">{product.name}</p>
                                        <div className="flex items-center gap-3 mt-2 text-sm">
                                            <span className="flex items-center gap-1 text-blue-600">
                                                <Snowflake className="w-3.5 h-3.5" />
                                                {product.coolingCapacity}
                                            </span>
                                        </div>
                                        <div className="mt-3 text-right">
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
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Link
                    href="/iletisim"
                    className="flex items-center justify-center gap-2 px-6 py-4 bg-blue-600 text-white font-semibold rounded-2xl hover:bg-blue-700 transition-colors shadow-lg"
                >
                    <Phone className="w-5 h-5" />
                    Keşif Talep Et
                </Link>
                <a
                    href="tel:02244131617"
                    className="flex items-center justify-center gap-2 px-6 py-4 border-2 border-blue-600 text-blue-600 font-semibold rounded-2xl hover:bg-blue-50 transition-colors"
                >
                    <Phone className="w-5 h-5" />
                    (0224) 413 16 17
                </a>
            </div>
        </div>
    )
}

// ===================== PROGRESS BAR =====================
function ProgressBar({ step, totalSteps }: { step: number; totalSteps: number }) {
    const percent = ((step) / totalSteps) * 100

    const stepLabels = ['Mekan', 'Boyut', 'Konum', 'Pencere', 'Kullanım', 'Sonuç']

    return (
        <div className="mb-8">
            {/* Step indicators */}
            <div className="flex items-center justify-between mb-3 px-1">
                {stepLabels.map((label, i) => (
                    <div key={i} className="flex flex-col items-center">
                        <div
                            className={`
                w-6 h-6 sm:w-8 sm:h-8 rounded-full flex items-center justify-center text-[10px] sm:text-xs font-bold transition-all duration-300
                ${i < step
                                    ? 'bg-blue-600 text-white'
                                    : i === step
                                        ? 'bg-blue-100 text-blue-700 ring-4 ring-blue-200'
                                        : 'bg-gray-100 text-gray-400'
                                }
              `}
                        >
                            {i < step ? '✓' : i + 1}
                        </div>
                        <span className={`text-xs mt-1 hidden sm:block ${i <= step ? 'text-blue-600 font-medium' : 'text-gray-400'}`}>
                            {label}
                        </span>
                    </div>
                ))}
            </div>

            {/* Progress bar */}
            <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                    className="h-full bg-gradient-to-r from-blue-500 to-blue-600 rounded-full transition-all duration-500 ease-out"
                    style={{ width: `${percent}%` }}
                />
            </div>
        </div>
    )
}

// ===================== MAIN WIZARD =====================
export default function KlimaSecWizard() {
    const [step, setStep] = useState(0)
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
            <div className="relative bg-blue-700 py-12 md:py-16">
                <div className="container mx-auto px-4 relative z-10">
                    <Link
                        href="/"
                        className="inline-flex items-center gap-2 text-white/80 hover:text-white mb-4 transition-colors"
                    >
                        <ArrowLeft className="w-4 h-4" />
                        Ana Sayfa
                    </Link>

                    <div className="flex items-center gap-4 mb-3">
                        <div className="w-14 h-14 bg-white/20 rounded-2xl flex items-center justify-center">
                            <Calculator className="w-8 h-8 text-white" />
                        </div>
                        <div>
                            <h1 className="text-3xl md:text-4xl font-bold text-white">Klimanı Seç</h1>
                            <p className="text-blue-200">Klima kapasite hesaplayıcı</p>
                        </div>
                    </div>

                    <p className="text-white/80 max-w-xl">
                        Birkaç soruya yanıt vererek odanıza en uygun klimayı bulun. Hesaplama sadece 1 dakika sürer!
                    </p>
                </div>
            </div>

            {/* Content */}
            <div className="container mx-auto px-4 py-8 md:py-12">
                <div className="max-w-2xl mx-auto">
                    <ProgressBar step={step} totalSteps={totalSteps} />

                    {/* Step Content */}
                    <div className="bg-white rounded-3xl shadow-sm border border-gray-100 p-6 md:p-10 mb-6">
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
                    <div className="flex items-center justify-between">
                        {step > 0 && step < 5 ? (
                            <button
                                onClick={prevStep}
                                className="inline-flex items-center gap-2 px-5 py-3 text-gray-600 hover:text-gray-900 font-medium rounded-xl hover:bg-gray-100 transition-all"
                            >
                                <ArrowLeft className="w-4 h-4" />
                                Geri
                            </button>
                        ) : step === 5 ? (
                            <button
                                onClick={reset}
                                className="inline-flex items-center gap-2 px-5 py-3 text-gray-600 hover:text-gray-900 font-medium rounded-xl hover:bg-gray-100 transition-all"
                            >
                                <RotateCcw className="w-4 h-4" />
                                Yeniden Hesapla
                            </button>
                        ) : (
                            <div />
                        )}

                        {step < 4 && (
                            <button
                                onClick={nextStep}
                                disabled={!canProceed}
                                className={`
                  inline-flex items-center gap-2 px-8 py-3 font-semibold rounded-xl transition-all duration-200 shadow-lg
                  ${canProceed
                                        ? 'bg-blue-600 text-white hover:bg-blue-700 hover:shadow-xl'
                                        : 'bg-gray-200 text-gray-400 cursor-not-allowed shadow-none'
                                    }
                `}
                            >
                                Devam
                                <ArrowRight className="w-4 h-4" />
                            </button>
                        )}

                        {step === 4 && (
                            <button
                                onClick={nextStep}
                                disabled={!canProceed}
                                className={`
                  inline-flex items-center gap-2 px-8 py-3 font-semibold rounded-xl transition-all duration-200 shadow-lg
                  ${canProceed
                                        ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white hover:from-blue-700 hover:to-indigo-700 hover:shadow-xl'
                                        : 'bg-gray-200 text-gray-400 cursor-not-allowed shadow-none'
                                    }
                `}
                            >
                                <Calculator className="w-4 h-4" />
                                Hesapla
                            </button>
                        )}
                    </div>
                </div>
            </div>
        </main>
    )
}
