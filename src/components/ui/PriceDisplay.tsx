'use client'

import { useEffect, useState, useRef } from 'react'

interface PriceDisplayProps {
  model: string
  className?: string
}

interface PriceCache {
  data: Record<string, number>
  timestamp: number
}

const CACHE_DURATION = 5 * 60 * 1000

function getCachedPrices(): Record<string, number> | null {
  if (typeof window === 'undefined') return null
  
  try {
    const cached = sessionStorage.getItem('vedel_prices')
    if (cached) {
      const parsed: PriceCache = JSON.parse(cached)
      if (Date.now() - parsed.timestamp < CACHE_DURATION) {
        return parsed.data
      }
    }
  } catch {}
  return null
}

function setCachedPrices(data: Record<string, number>) {
  if (typeof window === 'undefined') return
  
  try {
    const cache: PriceCache = {
      data,
      timestamp: Date.now()
    }
    sessionStorage.setItem('vedel_prices', JSON.stringify(cache))
  } catch {}
}

let priceFetchPromise: Promise<Record<string, number>> | null = null

async function fetchPrices(): Promise<Record<string, number>> {
  if (priceFetchPromise) {
    return priceFetchPromise
  }

  const cached = getCachedPrices()
  if (cached) {
    priceFetchPromise = Promise.resolve(cached)
    return priceFetchPromise
  }

  priceFetchPromise = fetch('/api/prices')
    .then(res => {
      if (!res.ok) throw new Error('Failed to fetch prices')
      return res.json()
    })
    .then(data => {
      setCachedPrices(data)
      return data
    })
    .catch(err => {
      priceFetchPromise = null
      throw err
    })

  return priceFetchPromise
}

function findPrice(prices: Record<string, number>, model: string): number | null {
  const cleanModel = model.toUpperCase().replace(/-/g, '').replace(/ /g, '')
  const originalModelUpper = model.toUpperCase()
  
  if (prices[originalModelUpper]) {
    return prices[originalModelUpper]
  }

  const exactCleanMatch = Object.entries(prices).find(
    ([key]) => key.toUpperCase().replace(/-/g, '').replace(/ /g, '') === cleanModel
  )
  
  if (exactCleanMatch) {
    return exactCleanMatch[1]
  }

  for (const [key, value] of Object.entries(prices)) {
    const cleanKey = key.toUpperCase().replace(/-/g, '').replace(/ /g, '')
    if (cleanKey.includes(cleanModel) || cleanModel.includes(cleanKey)) {
      return value
    }
  }

  return null
}

export default function PriceDisplay({ model, className = '' }: PriceDisplayProps) {
  const [price, setPrice] = useState<number | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)
  const mountedRef = useRef(true)

  useEffect(() => {
    mountedRef.current = true

    const loadPrice = async () => {
      try {
        const prices = await fetchPrices()
        
        if (!mountedRef.current) return
        
        const foundPrice = findPrice(prices, model)
        setPrice(foundPrice)
        setError(foundPrice === null)
      } catch (err) {
        if (!mountedRef.current) return
        console.error('Price fetch error:', err)
        setError(true)
      } finally {
        if (mountedRef.current) {
          setLoading(false)
        }
      }
    }

    if (model) {
      loadPrice()
    }

    return () => {
      mountedRef.current = false
    }
  }, [model])

  if (loading) {
    return (
      <span className={className}>
        Yükleniyor...
      </span>
    )
  }

  if (error || price === null) {
    return (
      <span className={className}>
        Fiyat bilgisi için arayınız
      </span>
    )
  }

  return (
    <span className={className}>
      {price.toLocaleString('tr-TR')} TL
    </span>
  )
}
