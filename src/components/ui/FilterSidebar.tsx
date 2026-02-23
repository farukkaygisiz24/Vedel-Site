'use client'

import { useState, useEffect } from 'react'
import { SlidersHorizontal, X, ChevronDown } from 'lucide-react'

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
}

const BTU_OPTIONS = [
  { value: 9000, label: '9.000 BTU' },
  { value: 12000, label: '12.000 BTU' },
  { value: 18000, label: '18.000 BTU' },
  { value: 22000, label: '22.000 BTU' },
  { value: 24000, label: '24.000 BTU' },
  { value: 30000, label: '30.000 BTU' },
]

const PRICE_RANGES = [
  { min: 0, max: 50000, label: '50.000 TL altı' },
  { min: 50000, max: 70000, label: '50.000 - 70.000 TL' },
  { min: 70000, max: 100000, label: '70.000 - 100.000 TL' },
  { min: 100000, max: 999999, label: '100.000 TL üstü' },
]

const ENERGY_CLASSES = ['A+++', 'A++', 'A+', 'A']

export default function FilterSidebar({ products, onFilterChange }: FilterSidebarProps) {
  const [prices, setPrices] = useState<Record<string, number>>({})
  const [loading, setLoading] = useState(true)
  
  const [selectedBtu, setSelectedBtu] = useState<number[]>([])
  const [selectedPriceRange, setSelectedPriceRange] = useState<number>(-1)
  const [selectedEnergy, setSelectedEnergy] = useState<string[]>([])
  const [sortBy, setSortBy] = useState<'price-asc' | 'price-desc' | 'btu-asc' | 'btu-desc'>('price-asc')
  const [isMobileOpen, setIsMobileOpen] = useState(false)

  useEffect(() => {
    fetch('/api/prices')
      .then(res => res.json())
      .then(data => {
        setPrices(data)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  useEffect(() => {
    let filtered = [...products]

    if (selectedBtu.length > 0) {
      filtered = filtered.filter(p => selectedBtu.includes(p.btu))
    }

    if (selectedPriceRange >= 0) {
      const range = PRICE_RANGES[selectedPriceRange]
      filtered = filtered.filter(p => {
        const price = prices[p.model] || 0
        return price >= range.min && price <= range.max
      })
    }

    if (selectedEnergy.length > 0) {
      filtered = filtered.filter(p => selectedEnergy.includes(p.energyClass))
    }

    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'price-asc':
          return (prices[a.model] || 0) - (prices[b.model] || 0)
        case 'price-desc':
          return (prices[b.model] || 0) - (prices[a.model] || 0)
        case 'btu-asc':
          return a.btu - b.btu
        case 'btu-desc':
          return b.btu - a.btu
        default:
          return 0
      }
    })

    onFilterChange(filtered)
  }, [products, selectedBtu, selectedPriceRange, selectedEnergy, sortBy, prices, onFilterChange])

  const clearFilters = () => {
    setSelectedBtu([])
    setSelectedPriceRange(-1)
    setSelectedEnergy([])
    setSortBy('price-asc')
  }

  const hasActiveFilters = selectedBtu.length > 0 || selectedPriceRange >= 0 || selectedEnergy.length > 0

  return (
    <>
      <button 
        onClick={() => setIsMobileOpen(true)}
        className="lg:hidden fixed bottom-6 right-6 z-50 flex items-center gap-2 px-6 py-3 bg-blue-600 text-white font-semibold rounded-full shadow-lg hover:bg-blue-700 transition-colors"
      >
        <SlidersHorizontal className="w-5 h-5" />
        Filtrele
        {hasActiveFilters && (
          <span className="w-5 h-5 bg-red-500 rounded-full text-xs flex items-center justify-center">
            {selectedBtu.length + (selectedPriceRange >= 0 ? 1 : 0) + selectedEnergy.length}
          </span>
        )}
      </button>

      <aside className={`
        fixed lg:static inset-0 z-50 lg:z-auto
        bg-white lg:bg-transparent
        transition-transform duration-300
        ${isMobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        w-full lg:w-64 lg:flex-shrink-0
        overflow-y-auto
      `}>
        <div className="p-6 lg:p-0">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-bold text-gray-900">Filtrele</h3>
            <button onClick={() => setIsMobileOpen(false)} className="lg:hidden p-2">
              <X className="w-5 h-5" />
            </button>
          </div>

          {hasActiveFilters && (
            <button
              onClick={clearFilters}
              className="w-full mb-4 px-4 py-2 text-sm text-red-600 border border-red-200 rounded-lg hover:bg-red-50 transition-colors"
            >
              Filtreleri Temizle
            </button>
          )}

          <div className="mb-6">
            <h4 className="text-sm font-semibold text-gray-700 mb-3">BTU Kapasitesi</h4>
            <div className="space-y-2">
              {BTU_OPTIONS.map(option => (
                <label key={option.value} className="flex items-center gap-2 cursor-pointer">
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
                    className="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-600">{option.label}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="mb-6">
            <h4 className="text-sm font-semibold text-gray-700 mb-3">Fiyat Aralığı</h4>
            <div className="space-y-2">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="price"
                  checked={selectedPriceRange === -1}
                  onChange={() => setSelectedPriceRange(-1)}
                  className="w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-600">Tümü</span>
              </label>
              {PRICE_RANGES.map((range, idx) => (
                <label key={idx} className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="price"
                    checked={selectedPriceRange === idx}
                    onChange={() => setSelectedPriceRange(idx)}
                    className="w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-600">{range.label}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="mb-6">
            <h4 className="text-sm font-semibold text-gray-700 mb-3">Enerji Sınıfı</h4>
            <div className="space-y-2">
              {ENERGY_CLASSES.map(cls => (
                <label key={cls} className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={selectedEnergy.includes(cls)}
                    onChange={e => {
                      if (e.target.checked) {
                        setSelectedEnergy([...selectedEnergy, cls])
                      } else {
                        setSelectedEnergy(selectedEnergy.filter(e => e !== cls))
                      }
                    }}
                    className="w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-600">{cls}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="mb-6">
            <h4 className="text-sm font-semibold text-gray-700 mb-3">Sırala</h4>
            <div className="relative">
              <select
                value={sortBy}
                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                onChange={e => setSortBy(e.target.value as any)}
                className="w-full px-4 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none bg-white"
              >
                <option value="price-asc">Fiyat (Düşük → Yüksek)</option>
                <option value="price-desc">Fiyat (Yüksek → Düşük)</option>
                <option value="btu-asc">BTU (Küçük → Büyük)</option>
                <option value="btu-desc">BTU (Büyük → Küçük)</option>
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
            </div>
          </div>
        </div>
      </aside>

      {isMobileOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setIsMobileOpen(false)}
        />
      )}
    </>
  )
}
