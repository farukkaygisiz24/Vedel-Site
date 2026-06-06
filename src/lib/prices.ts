const CACHE_DURATION = 5 * 60 * 1000
const FETCH_TIMEOUT_MS = 5000

interface PriceCache {
  data: Record<string, number>
  timestamp: number
}

/** MHI multi duvar tipi iç üniteler — sheet'te "MODEL ic" satırından fiyat alınır */
const MHI_MULTI_INDOOR_IC = /^(SRK(20|25|35|50)ZS-W|SRK60ZSX-W)$/i

export function getCachedPrices(): Record<string, number> | null {
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

export function setCachedPrices(data: Record<string, number>) {
  if (typeof window === 'undefined') return

  try {
    const cache: PriceCache = {
      data,
      timestamp: Date.now(),
    }
    sessionStorage.setItem('vedel_prices', JSON.stringify(cache))
  } catch {}
}

let priceFetchPromise: Promise<Record<string, number>> | null = null

export async function fetchPrices(): Promise<Record<string, number>> {
  if (priceFetchPromise) {
    return priceFetchPromise
  }

  const cached = getCachedPrices()
  if (cached) {
    return cached
  }

  priceFetchPromise = (async () => {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS)

    try {
      const res = await fetch('/api/prices', { signal: controller.signal })
      if (!res.ok) throw new Error('Failed to fetch prices')
      const data = await res.json()
      if (data && typeof data === 'object' && !data.error) {
        setCachedPrices(data)
        return data as Record<string, number>
      }
      throw new Error('Invalid price data')
    } catch {
      return getCachedPrices() ?? {}
    } finally {
      clearTimeout(timeoutId)
      priceFetchPromise = null
    }
  })()

  return priceFetchPromise
}

function normalizePriceKey(key: string): string {
  return key.toUpperCase().replace(/-/g, '').replace(/ /g, '')
}

function lookupPrice(prices: Record<string, number>, key: string): number | null {
  if (prices[key] !== undefined) return prices[key]

  const clean = normalizePriceKey(key)
  const found = Object.entries(prices).find(([k]) => normalizePriceKey(k) === clean)
  return found ? found[1] : null
}

function buildPriceLookupKeys(model: string, brand?: string): string[] {
  const upper = model.toUpperCase()
  const keys: string[] = []

  // Sheet'te aynı kod Premium ve Multi bölümlerinde tekrar ediyor; multi iç ünite " ic" satırı doğru fiyat
  if (brand === 'mhi_multi' && MHI_MULTI_INDOOR_IC.test(model)) {
    keys.push(`${upper} IC`)
  }

  keys.push(upper)
  return keys
}

export function findPrice(
  prices: Record<string, number>,
  model: string,
  brand?: string
): number | null {
  for (const key of buildPriceLookupKeys(model, brand)) {
    const price = lookupPrice(prices, key)
    if (price !== null) return price
  }
  return null
}

export function getProductPrice(
  prices: Record<string, number>,
  model: string,
  brand?: string
): number {
  return findPrice(prices, model, brand) ?? 0
}
