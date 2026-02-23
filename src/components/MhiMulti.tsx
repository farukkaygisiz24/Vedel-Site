'use client'

import { useState, useMemo } from 'react'
import Image from 'next/image'
import Link from 'next/link'
import { ArrowLeft, Snowflake, Flame, Zap, Wind, Clock, Shield, Star, Calculator } from 'lucide-react'
import PriceDisplay from '@/components/ui/PriceDisplay'
import FilterSidebar from '@/components/ui/FilterSidebar'

function CalculatorBanner() {
  return (
    <div className="my-8 bg-gradient-to-r from-blue-600 to-blue-700 rounded-2xl p-6 md:p-8 text-white shadow-lg">
      <div className="flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 bg-white/20 rounded-xl flex items-center justify-center">
            <Calculator className="w-8 h-8" />
          </div>
          <div>
            <h3 className="text-xl font-bold">🤔 Multi Klima Seçiminde Zorlanıyor musunuz?</h3>
            <p className="text-blue-100 mt-1">İç ünitelerinizi seçin, size uygun dış üniteyi ve fiyatı otomatik hesaplayalım!</p>
          </div>
        </div>
        <Link
          href="/urunler/multisistemler/mhi/hesaplayici"
          className="shrink-0 inline-flex items-center gap-2 px-6 py-3 bg-white text-blue-700 font-semibold rounded-xl hover:bg-blue-50 transition-colors"
        >
          Hesaplayıcıya Git
          <ArrowLeft className="w-4 h-4 rotate-180" />
        </Link>
      </div>
    </div>
  )
}

interface Product {
  id: string
  model: string
  name: string
  btu: number
  energyClass: string
  coolingCapacity: string
  heatingCapacity: string
  image: string
}

interface MhiMultiData {
  brand: string
  logo: string
  description: string
  categories: {
    outdoor: Product[]
    indoor_wall: Product[]
    cassette: Product[]
    ducted: Product[]
  }
}

function ProductCard({ product, brand }: { product: Product; brand: string }) {
  const modelParam = product.model.replace('-SET', '')

  return (
    <Link href={`/urunler/${brand}/${modelParam}`}>
      <div className="group bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-xl hover:-translate-y-1 transition-all duration-300 h-full">
        <div className="relative h-48 p-4 bg-gray-50">
          <Image
            src={product.image}
            alt={product.model}
            fill
            className="object-contain group-hover:scale-105 transition-transform duration-300"
          />
        </div>
        <div className="p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <span className="inline-block px-3 py-1 bg-red-100 text-red-700 text-xs font-bold rounded-full mb-2">
                {product.btu} BTU
              </span>
              <h3 className="text-lg font-bold text-gray-900">{product.model}</h3>
              <p className="text-sm text-gray-500">{product.name}</p>
            </div>
            <div className="flex items-center gap-1 bg-green-100 text-green-700 px-2 py-1 rounded-lg">
              <Zap className="w-4 h-4" />
              <span className="text-sm font-bold">{product.energyClass}</span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3 mb-4">
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Snowflake className="w-4 h-4 text-blue-500" />
              <span>Soğutma</span>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Flame className="w-4 h-4 text-orange-500" />
              <span>Isıtma</span>
            </div>
          </div>

          <div className="border-t border-gray-100 pt-4 mt-auto">
            <div className="flex items-center justify-between">
              <PriceDisplay
                model={product.model}
                className="text-lg font-bold text-red-600"
              />
              <span className="text-sm text-red-600 font-medium group-hover:translate-x-1 transition-transform">
                İncele →
              </span>
            </div>
          </div>
        </div>
      </div>
    </Link>
  )
}

export default function MhiMultiClient({ data }: { data: MhiMultiData }) {
  const allProducts = useMemo(() => {
    const products: Product[] = []
    if (data.categories.outdoor) products.push(...data.categories.outdoor)
    if (data.categories.indoor_wall) products.push(...data.categories.indoor_wall)
    if (data.categories.cassette) products.push(...data.categories.cassette)
    if (data.categories.ducted) products.push(...data.categories.ducted)
    return products
  }, [data])

  const [filteredProducts, setFilteredProducts] = useState<Product[]>(allProducts)

  const categories = [
    { key: 'outdoor', title: 'Dış Üniteler', desc: 'Tek dış üniteye birden fazla iç ünite bağlayın', products: data.categories.outdoor || [] },
    { key: 'indoor_wall', title: 'Duvar Tipi İç Üniteler', desc: 'Klasik duvar tipi iç üniteler', products: data.categories.indoor_wall || [] },
    { key: 'cassette', title: 'Kaset Tipi', desc: 'Tavana monte kaset tipi üniteler', products: data.categories.cassette || [] },
    { key: 'ducted', title: 'Kanal Tipi', desc: 'Gizli montaj kanal tipi üniteler', products: data.categories.ducted || [] },
  ]

  return (
    <div className="container mx-auto px-4 py-12 md:py-16">
      <div className="flex flex-col lg:flex-row gap-8">
        <div className="hidden lg:block w-64 flex-shrink-0">
          <div className="sticky top-24">
            <FilterSidebar
              products={allProducts}
              onFilterChange={setFilteredProducts}
            />
          </div>
        </div>
        {/* Mobile filter */}
        <div className="lg:hidden">
          <FilterSidebar
            products={allProducts}
            onFilterChange={setFilteredProducts}
          />
        </div>

        <div className="flex-1">
          <CalculatorBanner />

          <div className="mb-6 flex items-center justify-between">
            <p className="text-gray-500">
              <span className="font-semibold text-gray-900">{filteredProducts.length}</span> ürün bulundu
            </p>
          </div>

          {categories.map(({ key, title, desc, products: categoryProducts }) => {
            const filteredCategoryProducts = filteredProducts.filter(p =>
              categoryProducts.some(cp => cp.id === p.id)
            )

            if (filteredCategoryProducts.length === 0) return null

            return (
              <section key={key} className="mb-12">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
                    <p className="text-gray-500">{desc}</p>
                  </div>
                  <span className="text-sm text-gray-400">{filteredCategoryProducts.length} ürün</span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                  {filteredCategoryProducts.map((product) => (
                    <ProductCard key={product.id} product={product} brand="mhi_multi" />
                  ))}
                </div>
              </section>
            )
          })}

          {filteredProducts.length === 0 && (
            <div className="text-center py-12">
              <p className="text-gray-500 text-lg">Filtrelere uygun ürün bulunamadı.</p>
            </div>
          )}
        </div>
      </div>

      <div className="mt-16 bg-white rounded-2xl p-8 md:p-12 shadow-sm border border-gray-100">
        <div className="grid md:grid-cols-2 gap-8 items-center">
          <div>
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              Size Özel Teklif İster misiniz?
            </h3>
            <p className="text-gray-600 mb-6">
              Uzman ekibimiz ihtiyaçlarınızı analiz ederek en uygun multi klima çözümünü sunmaktadır.
            </p>
            <Link
              href="/iletisim"
              className="inline-flex items-center gap-2 px-6 py-3 bg-red-600 text-white font-semibold rounded-xl hover:bg-red-700 transition-colors"
            >
              İletişime Geç
              <ArrowLeft className="w-4 h-4 rotate-180" />
            </Link>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gray-50 rounded-xl p-4 text-center">
              <Wind className="w-8 h-8 text-blue-500 mx-auto mb-2" />
              <p className="text-sm text-gray-600">Profesyonel Montaj</p>
            </div>
            <div className="bg-gray-50 rounded-xl p-4 text-center">
              <Shield className="w-8 h-8 text-green-500 mx-auto mb-2" />
              <p className="text-sm text-gray-600">Garanti Destek</p>
            </div>
            <div className="bg-gray-50 rounded-xl p-4 text-center">
              <Clock className="w-8 h-8 text-purple-500 mx-auto mb-2" />
              <p className="text-sm text-gray-600">7/24 Servis</p>
            </div>
            <div className="bg-gray-50 rounded-xl p-4 text-center">
              <Star className="w-8 h-8 text-yellow-500 mx-auto mb-2" />
              <p className="text-sm text-gray-600">Kalite Belgeli</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
