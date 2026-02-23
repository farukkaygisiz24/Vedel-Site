'use client'

import { useState, useMemo, useEffect } from 'react'
import Image from 'next/image'
import Link from 'next/link'
import { ArrowLeft, Snowflake, Plus, Minus, Check, Calculator, Warehouse, Wind, ChevronRight, AlertTriangle, Package, ExternalLink } from 'lucide-react'
import productsData from '@/data/products.json'

interface IndoorProduct {
  id: string
  model: string
  name: string
  btu: number
  coolingCapacity: string
  heatingCapacity: string
  energyClass: string
  image: string
  category: 'indoor_wall' | 'cassette' | 'ducted'
}

interface OutdoorProduct {
  id: string
  model: string
  name: string
  btu: number
  coolingCapacity: string
  heatingCapacity: string
  energyClass: string
  maxIndoor: string
  image: string
}

interface SelectedIndoor {
  product: IndoorProduct
  quantity: number
}

interface PriceData {
  [key: string]: number
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const products = productsData as any

const indoorCategories = [
  { key: 'indoor_wall', title: 'Duvar Tipi İç Üniteler', icon: <Warehouse className="w-5 h-5" /> },
  { key: 'cassette', title: 'Kaset Tipi İç Üniteler', icon: <Snowflake className="w-5 h-5" /> },
  { key: 'ducted', title: 'Kanal Tipi İç Üniteler', icon: <Wind className="w-5 h-5" /> },
]

export default function MultiHesaplayiciPage() {
  const [selectedIndoors, setSelectedIndoors] = useState<SelectedIndoor[]>([])
  const [prices, setPrices] = useState<PriceData>({})
  const [pricesLoading, setPricesLoading] = useState(true)
  const [showResult, setShowResult] = useState(false)

  useEffect(() => {
    const fetchPrices = async () => {
      try {
        const response = await fetch('/api/prices')
        const data: PriceData = await response.json()
        setPrices(data)
      } catch (error) {
        console.error('Fiyatlar yüklenemedi:', error)
      } finally {
        setPricesLoading(false)
      }
    }
    fetchPrices()
  }, [])

  const indoorProducts = useMemo(() => {
    const all: IndoorProduct[] = []

    if (products.mhi_multi?.categories?.indoor_wall) {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      products.mhi_multi.categories.indoor_wall.forEach((p: any) => {
        all.push({ ...p, category: 'indoor_wall' as const })
      })
    }
    if (products.mhi_multi?.categories?.cassette) {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      products.mhi_multi.categories.cassette.forEach((p: any) => {
        all.push({ ...p, category: 'cassette' as const })
      })
    }
    if (products.mhi_multi?.categories?.ducted) {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      products.mhi_multi.categories.ducted.forEach((p: any) => {
        all.push({ ...p, category: 'ducted' as const })
      })
    }

    return all
  }, [])

  const outdoorProducts = useMemo(() => {
    return products.mhi_multi?.categories?.outdoor || []
  }, [])

  const getPrice = (model: string): number | null => {
    const cleanModel = model.toUpperCase().replace(/-/g, '').replace(/ /g, '')
    if (prices[cleanModel]) return prices[cleanModel]
    for (const [key, value] of Object.entries(prices)) {
      const cleanKey = key.toUpperCase().replace(/-/g, '').replace(/ /g, '')
      if (cleanKey.includes(cleanModel) || cleanModel.includes(cleanKey)) {
        return value
      }
    }
    return null
  }

  const formatPrice = (price: number | null): string => {
    if (price === null) return 'Fiyat için arayınız'
    return `${price.toLocaleString('tr-TR')} TL`
  }

  const handleQuantityChange = (product: IndoorProduct, delta: number) => {
    setSelectedIndoors(prev => {
      const existing = prev.find(item => item.product.id === product.id)

      if (delta > 0) {
        if (existing) {
          return prev.map(item =>
            item.product.id === product.id
              ? { ...item, quantity: item.quantity + 1 }
              : item
          )
        } else {
          return [...prev, { product, quantity: 1 }]
        }
      } else {
        if (existing && existing.quantity > 1) {
          return prev.map(item =>
            item.product.id === product.id
              ? { ...item, quantity: item.quantity - 1 }
              : item
          )
        } else {
          return prev.filter(item => item.product.id !== product.id)
        }
      }
    })
    setShowResult(false)
  }

  const getQuantity = (productId: string): number => {
    const found = selectedIndoors.find(item => item.product.id === productId)
    return found?.quantity || 0
  }

  const totalBTU = useMemo(() => {
    return selectedIndoors.reduce((sum, item) => sum + (item.product.btu * item.quantity), 0)
  }, [selectedIndoors])

  const totalIndoorUnits = useMemo(() => {
    return selectedIndoors.reduce((sum, item) => sum + item.quantity, 0)
  }, [selectedIndoors])

  const totalIndoorPrice = useMemo(() => {
    return selectedIndoors.reduce((sum, item) => {
      const price = getPrice(item.product.model)
      return sum + (price !== null ? price * item.quantity : 0)
    }, 0)
  }, [selectedIndoors, prices])

  const recommendedOutdoor = useMemo(() => {
    if (totalIndoorUnits === 0) return null

    // 1. Filter out outdoor units that cannot support the number of indoor units (Strict Max Indoor check)
    const suitableOutdoors = outdoorProducts.filter((outdoor: OutdoorProduct) => {
      const maxUnits = parseInt(outdoor.maxIndoor.replace(' ünite', ''))
      return totalIndoorUnits <= maxUnits
    })

    if (suitableOutdoors.length === 0) return null

    // 2. Sort by BTU (High to Low) to prioritize LARGER units.
    // This reduces the capacity usage percentage (IndoorBTU / OutdoorBTU).
    suitableOutdoors.sort((a: OutdoorProduct, b: OutdoorProduct) => b.btu - a.btu)

    // 3. Return the largest suitable unit as the recommendation
    const best = suitableOutdoors[0]

    return {
      product: best,
      capacityPercent: Math.round((totalBTU / best.btu) * 100),
      isOptimal: true
    }
  }, [totalBTU, totalIndoorUnits, outdoorProducts])

  const alternativeOutdoors = useMemo(() => {
    if (!recommendedOutdoor) return []

    return outdoorProducts
      .filter((outdoor: OutdoorProduct) => {
        const maxUnits = parseInt(outdoor.maxIndoor.replace(' ünite', ''))
        if (totalIndoorUnits > maxUnits) return false
        if (outdoor.id === recommendedOutdoor.product.id) return false
        return true
      })
      .map((outdoor: OutdoorProduct) => ({
        product: outdoor,
        capacityPercent: Math.round((totalBTU / outdoor.btu) * 100)
      }))
      .sort((a: { capacityPercent: number }, b: { capacityPercent: number }) => a.capacityPercent - b.capacityPercent) // Sort by lowest percentage first (largest units)
  }, [recommendedOutdoor, totalBTU, totalIndoorUnits, outdoorProducts])

  const totalSystemPrice = useMemo(() => {
    if (!recommendedOutdoor) return totalIndoorPrice
    const outdoorPrice = getPrice(recommendedOutdoor.product.model)
    return totalIndoorPrice + (outdoorPrice !== null ? outdoorPrice : 0)
  }, [recommendedOutdoor, totalIndoorPrice, prices])

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Hero Section - BLUE THEME */}
      <div className="relative bg-gradient-to-r from-blue-700 to-blue-600 py-16 md:py-24 overflow-hidden">
        <div className="absolute inset-0 bg-black/20"></div>
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-10 left-10 w-32 h-32 border border-white rounded-full"></div>
          <div className="absolute bottom-10 right-10 w-48 h-48 border border-white rounded-full"></div>
          <div className="absolute top-1/2 left-1/3 w-24 h-24 border border-white rounded-full"></div>
        </div>

        <div className="container mx-auto px-4 relative z-10">
          <div className="flex flex-col gap-6">
            <Link
              href="/urunler/multisistemler/mhi"
              className="inline-flex items-center gap-2 text-white/80 hover:text-white transition-colors w-fit group"
            >
              <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
              Multi Sistemlere Dön
            </Link>

            <div className="flex items-center gap-4">
              <div className="w-16 h-16 bg-white/10 backdrop-blur-sm rounded-2xl flex items-center justify-center border border-white/20 shadow-xl">
                <Calculator className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-3xl md:text-4xl font-bold text-white mb-2">
                  Multi Klima Hesaplayıcı
                </h1>
                <p className="text-blue-100/90 text-lg flex items-center gap-2">
                  Mitsubishi Heavy Industries
                  <span className="w-1.5 h-1.5 rounded-full bg-white/50"></span>
                  İhtiyacınıza Uygun Çözümler
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8 -mt-8 relative z-20">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Selection Column */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white rounded-2xl shadow-xl shadow-gray-200/50 border border-gray-100 p-6 md:p-8">
              <div className="flex items-center gap-4 mb-6 pb-6 border-b border-gray-100">
                <div className="w-10 h-10 rounded-full bg-blue-50 flex items-center justify-center">
                  <Package className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-gray-900">İç Üniteleri Seçin</h2>
                  <p className="text-gray-500 text-sm mt-1">
                    İstediğiniz iç üniteleri ve adetlerini belirleyin.
                  </p>
                </div>
              </div>

              {indoorCategories.map(category => {
                const categoryProducts = indoorProducts.filter(p => p.category === category.key)
                if (categoryProducts.length === 0) return null

                return (
                  <div key={category.key} className="mb-8 last:mb-0">
                    <h3 className="font-semibold text-gray-800 mb-4 flex items-center gap-2 text-lg">
                      <span className="p-1.5 bg-gray-100 rounded-lg text-gray-600">{category.icon}</span>
                      {category.title}
                    </h3>
                    <div className="space-y-3">
                      {categoryProducts.map(product => {
                        const quantity = getQuantity(product.id)
                        const price = getPrice(product.model)

                        return (
                          <div
                            key={product.id}
                            className={`group relative flex items-center justify-between p-4 rounded-xl border transition-all duration-300 ${quantity > 0
                              ? 'bg-blue-50/50 border-blue-200 shadow-sm'
                              : 'bg-white border-gray-100 hover:border-blue-100 hover:shadow-md'
                              }`}
                          >
                            <div className="flex items-center gap-4">
                              <div className="relative w-20 h-20 bg-white rounded-lg p-2 flex-shrink-0 border border-gray-100 group-hover:scale-105 transition-transform">
                                <Image
                                  src={product.image}
                                  alt={product.model}
                                  fill
                                  className="object-contain"
                                />
                              </div>
                              <div>
                                <p className="font-bold text-gray-900 group-hover:text-blue-700 transition-colors">
                                  {product.model}
                                </p>
                                <p className="text-sm text-gray-500 mt-1">
                                  {product.btu.toLocaleString()} BTU • {product.name}
                                </p>
                                <p className="text-sm font-semibold text-blue-600 mt-1">
                                  {formatPrice(price)}
                                </p>
                              </div>
                            </div>

                            <div className="flex items-center gap-3 bg-white p-1 rounded-lg border border-gray-100 shadow-sm">
                              <button
                                onClick={() => handleQuantityChange(product, -1)}
                                disabled={quantity === 0}
                                className="w-8 h-8 rounded-md hover:bg-blue-50 disabled:opacity-30 disabled:hover:bg-transparent flex items-center justify-center transition-colors text-gray-600 hover:text-blue-600"
                              >
                                <Minus className="w-4 h-4" />
                              </button>
                              <span className={`w-8 text-center font-bold ${quantity > 0 ? 'text-blue-600' : 'text-gray-400'}`}>
                                {quantity}
                              </span>
                              <button
                                onClick={() => handleQuantityChange(product, 1)}
                                className="w-8 h-8 rounded-md bg-gray-50 hover:bg-blue-600 hover:text-white text-gray-600 flex items-center justify-center transition-all"
                              >
                                <Plus className="w-4 h-4" />
                              </button>
                            </div>
                          </div>
                        )
                      })}
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Sidebar Summary */}
          <div className="lg:col-span-1">
            <div className="sticky top-24 space-y-6">
              <div className="bg-white rounded-2xl shadow-xl shadow-gray-200/50 border border-gray-100 p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-3 pb-4 border-b border-gray-100">
                  <div className="w-9 h-9 rounded-full bg-blue-50 flex items-center justify-center flex-shrink-0">
                    <Calculator className="w-5 h-5 text-blue-600" />
                  </div>
                  Hesaplama Özeti
                </h2>

                <div className="space-y-4 mb-8">
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-gray-600">Seçili İç Ünite</span>
                    <span className="font-semibold text-gray-900 bg-gray-50 px-3 py-1 rounded-full">
                      {totalIndoorUnits} adet
                    </span>
                  </div>
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-gray-600">Toplam Kapasite</span>
                    <span className="font-semibold text-gray-900 bg-gray-50 px-3 py-1 rounded-full">
                      {totalBTU.toLocaleString()} BTU
                    </span>
                  </div>
                  <div className="flex justify-between items-center text-sm pt-4 border-t border-dashed border-gray-200">
                    <span className="text-gray-600 font-medium">İç Üniteler Toplamı</span>
                    <span className="font-bold text-gray-900">
                      {formatPrice(totalIndoorPrice)}
                    </span>
                  </div>
                </div>

                {selectedIndoors.length > 0 ? (
                  <button
                    onClick={() => setShowResult(true)}
                    className="w-full py-4 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-bold rounded-xl transition-all shadow-lg shadow-blue-200 hover:shadow-blue-300 transform hover:-translate-y-0.5 active:translate-y-0 flex items-center justify-center gap-2"
                  >
                    <Calculator className="w-5 h-5" />
                    Sistemi Hesapla
                  </button>
                ) : (
                  <div className="p-4 bg-gray-50 rounded-xl text-center text-gray-500 text-sm">
                    Hesaplama yapmak için lütfen iç ünite seçiniz.
                  </div>
                )}
              </div>

              {showResult && recommendedOutdoor && (
                <div className="bg-white rounded-2xl shadow-xl shadow-gray-200/50 border border-gray-100 p-6 animate-in slide-in-from-bottom-4 duration-500">

                  {recommendedOutdoor.capacityPercent > 130 ? (
                    <div className="p-4 bg-red-50 border border-red-200 rounded-xl mb-6">
                      <div className="flex items-center gap-2 mb-3">
                        <div className="w-8 h-8 rounded-full bg-red-100 flex items-center justify-center flex-shrink-0">
                          <AlertTriangle className="w-5 h-5 text-red-600" />
                        </div>
                        <span className="font-bold text-red-800 text-lg">Multi Klima Sistemi Önerilmez</span>
                      </div>

                      <div className="space-y-3 text-red-700">
                        <p className="font-medium">
                          Seçtiğiniz iç ünite kombinasyonunun toplam kapasitesi ({totalBTU.toLocaleString()} BTU),
                          bağlanabilecek en büyük dış ünite ({recommendedOutdoor.product.model}) kapasitesinin
                          <span className="font-bold underline decoration-red-400 mx-1">%{recommendedOutdoor.capacityPercent}</span>
                          seviyesindedir.
                        </p>
                        <p className="text-sm">
                          Multi split sistemlerde tavsiye edilen maksimum kapasite oranı %130&apos;dur. Bu oranın üzerinde sistem verimli çalışmayabilir ve performans kayıpları yaşanabilir.
                        </p>

                        <div className="bg-red-100/50 p-4 rounded-lg border border-red-200 mt-2">
                          <p className="text-sm font-semibold mb-2">Önerimiz:</p>
                          <ul className="list-disc list-inside text-sm space-y-1 ml-1 mb-4">
                            <li>İç ünite sayısını veya kapasitelerini azaltabilirsiniz.</li>
                            <li>Daha büyük projeler için <strong>VRF Sistemleri</strong> çözümlerimizi inceleyebilirsiniz.</li>
                          </ul>
                          <Link
                            href="/urunler/vrfsistemler"
                            className="w-full flex items-center justify-center gap-2 py-3 px-4 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-bold rounded-xl transition-all shadow-lg shadow-blue-200/50 hover:shadow-blue-300/50 transform hover:-translate-y-0.5 active:translate-y-0 text-sm"
                          >
                            <ExternalLink className="w-4 h-4" />
                            VRF Sistemlerini İncele
                          </Link>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className="p-4 bg-green-50 border border-green-100 rounded-xl mb-6">
                        <div className="flex items-center gap-2 mb-3">
                          <div className="w-6 h-6 rounded-full bg-green-100 flex items-center justify-center">
                            <Check className="w-4 h-4 text-green-600" />
                          </div>
                          <span className="font-bold text-green-800">Önerilen Dış Ünite</span>
                        </div>

                        <div className="relative w-full h-32 bg-white rounded-lg p-2 mb-4 border border-green-100 shadow-sm">
                          <Image
                            src={recommendedOutdoor.product.image}
                            alt={recommendedOutdoor.product.model}
                            fill
                            className="object-contain"
                          />
                        </div>

                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <p className="font-bold text-lg text-green-900">
                              {recommendedOutdoor.product.model}
                            </p>
                            <p className="text-sm text-green-700/80">
                              {recommendedOutdoor.product.btu.toLocaleString()} BTU
                            </p>
                            <p className="text-xs text-green-600 mt-1">
                              Maksimum {recommendedOutdoor.product.maxIndoor} bağlanabilir
                            </p>
                          </div>
                          <div className="text-right">
                            <span className={`inline-block px-2 py-1 rounded text-xs font-bold ${recommendedOutdoor.capacityPercent > 100
                              ? 'bg-red-100 text-red-700'
                              : recommendedOutdoor.isOptimal
                                ? 'bg-green-100 text-green-700'
                                : 'bg-yellow-100 text-yellow-700'
                              }`}>
                              %{recommendedOutdoor.capacityPercent} Kapasite
                            </span>
                          </div>
                        </div>

                        <div className="flex items-center justify-between pt-3 border-t border-green-200/60">
                          <span className="text-sm font-medium text-green-800">Cihaz Fiyatı</span>
                          <span className="font-bold text-green-900 text-lg">
                            {formatPrice(getPrice(recommendedOutdoor.product.model))}
                          </span>
                        </div>
                      </div>

                      {alternativeOutdoors.length > 0 && (
                        <div className="mb-6">
                          <h4 className="font-semibold text-gray-700 mb-3 text-sm flex items-center gap-2">
                            <ChevronRight className="w-4 h-4" /> Diğer Seçenekler
                          </h4>
                          <div className="space-y-2">
                            {alternativeOutdoors.slice(0, 2).map((alt: { product: OutdoorProduct; capacityPercent: number }) => (
                              <div key={alt.product.id} className="p-3 bg-gray-50 rounded-xl border border-gray-100 hover:border-gray-300 transition-colors">
                                <div className="flex justify-between items-center">
                                  <div>
                                    <p className="font-semibold text-gray-900 text-sm">{alt.product.model}</p>
                                    <p className="text-xs text-gray-500">
                                      {alt.product.btu.toLocaleString()} BTU
                                    </p>
                                  </div>
                                  <div className="text-right">
                                    <p className="text-xs font-medium text-gray-600 mb-0.5">
                                      %{alt.capacityPercent}
                                    </p>
                                    <p className="text-sm font-bold text-gray-900">
                                      {formatPrice(getPrice(alt.product.model))}
                                    </p>
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      <div className="p-5 bg-gradient-to-br from-gray-900 to-gray-800 text-white rounded-xl shadow-lg">
                        <div className="flex justify-between items-center mb-1">
                          <span className="text-gray-300 font-medium">Toplam Tutar</span>
                          <span className="text-2xl font-bold text-white">
                            {formatPrice(totalSystemPrice)}
                          </span>
                        </div>
                        <div className="text-right text-xs text-gray-400">
                          *KDV hariç tavsiye edilen perakende satış fiyatıdır.
                        </div>
                      </div>
                    </>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
