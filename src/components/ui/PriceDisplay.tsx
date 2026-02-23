'use client'

import { useEffect, useState } from 'react'

interface PriceDisplayProps {
  model: string
  className?: string
}

export default function PriceDisplay({ model, className = '' }: PriceDisplayProps) {
  const [price, setPrice] = useState<number | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)

  useEffect(() => {
    const fetchPrice = async () => {
      try {
        const cleanModel = model.toUpperCase().replace(/-/g, '').replace(/ /g, '')
        
        const response = await fetch('/api/prices')
        if (!response.ok) throw new Error('Failed to fetch')
        
        const prices: Record<string, number> = await response.json()
        
        let foundPrice: number | null = null
        
        if (prices[cleanModel]) {
          foundPrice = prices[cleanModel]
        } else {
          for (const [key, value] of Object.entries(prices)) {
            const cleanKey = key.toUpperCase().replace(/-/g, '').replace(/ /g, '')
            if (cleanKey.includes(cleanModel) || cleanModel.includes(cleanKey)) {
              foundPrice = value
              break
            }
          }
        }
        
        setPrice(foundPrice)
        setError(foundPrice === null)
      } catch (err) {
        console.error('Price fetch error:', err)
        setError(true)
      } finally {
        setLoading(false)
      }
    }

    if (model) {
      fetchPrice()
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
