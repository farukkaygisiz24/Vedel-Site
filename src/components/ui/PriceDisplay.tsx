'use client'

import { useEffect, useState, useRef } from 'react'
import { fetchPrices, findPrice, getCachedPrices } from '@/lib/prices'

interface PriceDisplayProps {
  model: string
  brand?: string
  className?: string
}

export default function PriceDisplay({ model, brand, className = '' }: PriceDisplayProps) {
  // SSR ve ilk client render aynı olmalı — cache sadece mount sonrası okunur
  const [price, setPrice] = useState<number | null>(null)
  const mountedRef = useRef(true)

  useEffect(() => {
    mountedRef.current = true

    const cached = getCachedPrices()
    const cachedPrice = cached ? findPrice(cached, model, brand) : null
    if (cachedPrice !== null) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setPrice(cachedPrice)
      return
    }

    fetchPrices()
      .then(prices => {
        if (!mountedRef.current) return
        setPrice(findPrice(prices, model, brand))
      })
      .catch(() => {})

    return () => {
      mountedRef.current = false
    }
  }, [model, brand])

  if (price === null) {
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
