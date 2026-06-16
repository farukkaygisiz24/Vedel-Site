'use client'

import { useState, useEffect } from 'react'
import { SlidersHorizontal, X, ChevronDown } from 'lucide-react'
import { fetchPrices, getCachedPrices, getProductPrice } from '@/lib/prices'

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

interface FilterSidebarProps {
  products: Product[]
  onFilterChange: (filtered: Product[]) => void
  brand: string
}

const BTU_OPTIONS = [
  { value: 9000, label: '9.000 BTU' },
  { value: 12000, label: '12.000 BTU' },
  { value: 18000, label: '18.000 BTU' },
  { value: 22000, label: '22.000 BTU' },
  { value: 24000, label: '24.000 BTU' },
]

const PRICE_RANGES = [
  { min: 0, max: 50000, label: '50.000 TL altı' },
  { min: 50000, max: 70000, label: '50.000 - 70.000 TL' },
  { min: 70000, max: 100000, label: '70.000 - 100.000 TL' },
  { min: 100000, max: 999999, label: '100.000 TL üstü' },
]

const ENERGY_CLASSES = ['A+++', 'A++', 'A+', 'A']

export default function FilterSidebar({ products, onFilterChange, brand }: FilterSidebarProps) {
  const [prices, setPrices] = useState<Record<string, number>>(
    () => getCachedPrices() ?? {}
  )
  const [isMounted, setIsMounted] = useState(false)
  const [pricesLoading, setPricesLoading] = useState(true)

  const [selectedBtu, setSelectedBtu] = useState<number[]>([])
  const [selectedPriceRange, setSelectedPriceRange] = useState<number>(-1)
  const [selectedEnergy, setSelectedEnergy] = useState<string[]>([])
  const [sortBy, setSortBy] = useState<'price-asc' | 'price-desc' | 'btu-asc' | 'btu-desc'>('price-asc')
  const [isMobileOpen, setIsMobileOpen] = useState(false)

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setIsMounted(true)
    fetchPrices()
      .then(data => {
        setPrices(data)
      })
      .catch(() => {})
      .finally(() => setPricesLoading(false))
  }, [])

  useEffect(() => {
    let filtered = [...products]

    if (selectedBtu.length > 0) {
      filtered = filtered.filter(p => selectedBtu.includes(p.btu))
    }

    if (selectedPriceRange >= 0) {
      const range = PRICE_RANGES[selectedPriceRange]
      filtered = filtered.filter(p => {
        const price = getProductPrice(prices, p.model, brand)
        return price >= range.min && price <= range.max
      })
    }

    if (selectedEnergy.length > 0) {
      filtered = filtered.filter(p => selectedEnergy.includes(p.energyClass))
    }

    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'price-asc':
          return getProductPrice(prices, a.model, brand) - getProductPrice(prices, b.model, brand)
        case 'price-desc':
          return getProductPrice(prices, b.model, brand) - getProductPrice(prices, a.model, brand)
        case 'btu-asc':
          return a.btu - b.btu
        case 'btu-desc':
          return b.btu - a.btu
        default:
          return 0
      }
    })

    onFilterChange(filtered)
  }, [products, selectedBtu, selectedPriceRange, selectedEnergy, sortBy, prices, brand, onFilterChange])

  useEffect(() => {
    if (isMobileOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
    return () => {
      document.body.style.overflow = ''
    }
  }, [isMobileOpen])

  const clearFilters = () => {
    setSelectedBtu([])
    setSelectedPriceRange(-1)
    setSelectedEnergy([])
    setSortBy('price-asc')
  }

  const hasActiveFilters = selectedBtu.length > 0 || selectedPriceRange >= 0 || selectedEnergy.length > 0
  const activeFilterCount = selectedBtu.length + (selectedPriceRange >= 0 ? 1 : 0) + selectedEnergy.length

  const optionLabelClass =
    'flex min-h-10 cursor-pointer items-center gap-2.5 rounded-lg px-1 active:bg-gray-50 lg:min-h-9'
  const sectionClass = 'mb-4 lg:mb-3.5'
  const sectionTitleClass = 'mb-2 text-xs font-bold uppercase tracking-wide text-gray-500'

  const filterSections = (
    <>
      {hasActiveFilters && (
        <button
          onClick={clearFilters}
          className="mb-4 w-full min-h-10 rounded-lg border border-red-200 px-4 py-2 text-sm text-red-600 transition-colors active:bg-red-50 md:hover:bg-red-50"
        >
          Filtreleri Temizle
        </button>
      )}

      <div className={sectionClass}>
        <h4 className={sectionTitleClass}>BTU Kapasitesi</h4>
        <div className="space-y-0.5">
          {BTU_OPTIONS.map(option => (
            <label key={option.value} className={optionLabelClass}>
              <input
                type="checkbox"
                checked={selectedBtu.includes(option.value)}
                onChange={e => {
                  if (e.target.checked) {
                    setSelectedBtu([...selectedBtu, option.value])
                  } else {
                    setSelectedBtu(selectedBtu.filter(b => b !== option.value))
                  }
                }}
                className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-600">{option.label}</span>
            </label>
          ))}
        </div>
      </div>

      <div className={sectionClass}>
        <h4 className={sectionTitleClass}>
          Fiyat Aralığı
          {pricesLoading && (
            <span className="ml-2 inline-block w-3 h-3 rounded-full border-2 border-gray-300 border-t-blue-500 animate-spin align-middle" />
          )}
        </h4>
        <div className="space-y-0.5">
          <label className={optionLabelClass}>
            <input
              type="radio"
              name="price"
              checked={selectedPriceRange === -1}
              onChange={() => setSelectedPriceRange(-1)}
              className="h-4 w-4 border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-600">Tümü</span>
          </label>
          {PRICE_RANGES.map((range, idx) => (
            <label key={idx} className={optionLabelClass}>
              <input
                type="radio"
                name="price"
                checked={selectedPriceRange === idx}
                onChange={() => setSelectedPriceRange(idx)}
                className="h-4 w-4 border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-600">{range.label}</span>
            </label>
          ))}
        </div>
      </div>

      <div className={sectionClass}>
        <h4 className={sectionTitleClass}>Enerji Sınıfı</h4>
        <div className="space-y-0.5">
          {ENERGY_CLASSES.map(cls => (
            <label key={cls} className={optionLabelClass}>
              <input
                type="checkbox"
                checked={selectedEnergy.includes(cls)}
                onChange={e => {
                  if (e.target.checked) {
                    setSelectedEnergy([...selectedEnergy, cls])
                  } else {
                    setSelectedEnergy(selectedEnergy.filter(c => c !== cls))
                  }
                }}
                className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-600">{cls}</span>
            </label>
          ))}
        </div>
      </div>

      <div>
        <h4 className={sectionTitleClass}>Sırala</h4>
        <div className="relative">
          <select
            value={sortBy}
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            onChange={e => setSortBy(e.target.value as any)}
            className="min-h-10 w-full appearance-none rounded-lg border border-gray-200 bg-white px-4 py-2 text-sm focus:border-transparent focus:ring-2 focus:ring-blue-500"
          >
            <option value="price-asc">Fiyat (Düşük → Yüksek)</option>
            <option value="price-desc">Fiyat (Yüksek → Düşük)</option>
            <option value="btu-asc">BTU (Küçük → Büyük)</option>
            <option value="btu-desc">BTU (Büyük → Küçük)</option>
          </select>
          <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
        </div>
      </div>
    </>
  )

  return (
    <>
      {isMounted && (
        <button
          onClick={() => setIsMobileOpen(true)}
          className="fixed bottom-5 right-4 z-50 flex min-h-12 items-center gap-2 rounded-full bg-blue-600 px-5 py-3 font-semibold text-white shadow-lg transition-colors active:bg-blue-700 sm:bottom-6 sm:right-6 md:hover:bg-blue-700 lg:hidden"
        >
          <SlidersHorizontal className="h-5 w-5" />
          Filtrele
          {hasActiveFilters && (
            <span className="flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-xs">
              {activeFilterCount}
            </span>
          )}
        </button>
      )}

      {isMounted && isMobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setIsMobileOpen(false)}
          aria-hidden="true"
        />
      )}

      <aside
        className={`
          fixed inset-y-0 right-0 z-50 flex w-full max-w-sm flex-col bg-white shadow-xl
          transition-transform duration-300 ease-out md:max-w-md
          lg:static lg:sticky lg:top-[calc(5rem+0.75rem)] lg:z-auto lg:w-full lg:max-w-none
          lg:max-h-[calc(100dvh-5rem-1.5rem)] lg:overflow-hidden
          lg:rounded-2xl lg:border lg:border-gray-200 lg:shadow-sm
          ${isMobileOpen ? 'translate-x-0' : 'translate-x-full lg:translate-x-0'}
        `}
      >
        <div className="flex shrink-0 items-center justify-between border-b border-gray-100 px-5 py-4 sm:px-6 lg:px-4 lg:py-3.5">
          <div className="flex items-center gap-2">
            <SlidersHorizontal className="h-5 w-5 text-gray-500" />
            <h3 className="text-base font-bold text-gray-900 lg:text-[0.9375rem]">Filtrele</h3>
          </div>
          <button
            onClick={() => setIsMobileOpen(false)}
            className="flex min-h-10 min-w-10 items-center justify-center rounded-lg lg:hidden"
            aria-label="Filtreleri kapat"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="filter-sidebar-scroll min-h-0 flex-1 overflow-y-auto overscroll-y-contain px-5 py-4 sm:px-6 lg:px-4 lg:py-3 lg:pb-6">
          {filterSections}
        </div>

        <div className="shrink-0 border-t border-gray-100 p-5 pt-3 sm:px-6 lg:hidden">
          <button
            onClick={() => setIsMobileOpen(false)}
            className="w-full min-h-12 rounded-xl bg-blue-600 py-3 font-semibold text-white transition-colors active:bg-blue-700 md:hover:bg-blue-700"
          >
            {filteredCountLabel(products.length, selectedBtu, selectedPriceRange, selectedEnergy)}
          </button>
        </div>
      </aside>
    </>
  )
}

function filteredCountLabel(
  total: number,
  selectedBtu: number[],
  selectedPriceRange: number,
  selectedEnergy: string[]
): string {
  const hasFilters = selectedBtu.length > 0 || selectedPriceRange >= 0 || selectedEnergy.length > 0
  return hasFilters ? 'Sonuçları Göster' : `${total} Ürünü Göster`
}
