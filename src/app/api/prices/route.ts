import { NextResponse } from 'next/server'

const SHEET_CSV_URL = process.env.PRICE_SHEET_URL || 'https://docs.google.com/spreadsheets/d/1p13kvy6wSne5sTlsVp_M5G_JU2pp1i7tDvImic11Nlk/export?format=csv'

interface RateLimitData {
  count: number
  resetTime: number
}

const rateLimitMap = new Map<string, RateLimitData>()
const RATE_LIMIT = 30
const RATE_LIMIT_WINDOW = 60 * 1000

function checkRateLimit(ip: string): boolean {
  const now = Date.now()
  const data = rateLimitMap.get(ip)
  
  if (!data || now > data.resetTime) {
    rateLimitMap.set(ip, { count: 1, resetTime: now + RATE_LIMIT_WINDOW })
    return true
  }
  
  if (data.count >= RATE_LIMIT) {
    return false
  }
  
  data.count++
  return true
}

interface CacheData {
  prices: Record<string, number>
  timestamp: number
}

let cache: CacheData | null = null
const CACHE_DURATION = 60 * 60 * 1000

async function fetchPricesFromSheet(): Promise<Record<string, number>> {
  const response = await fetch(SHEET_CSV_URL)
  if (!response.ok) {
    throw new Error('Failed to fetch sheet')
  }

  const csvText = await response.text()
  const lines = csvText.split('\n')
  
  const prices: Record<string, number> = {}
  
  for (const line of lines) {
    const parts = line.split(',')
    if (parts.length >= 2) {
      const model = parts[0].trim().replace(/"/g, '')
      const priceStr = parts[parts.length - 1].trim().replace(/"/g, '')
      
      if (model && model !== 'Model Kodu' && model !== 'MHI FİYAT LİSTESİ' && model !== 'EUROFORM FİYAT LİSTESİ') {
        const price = parseInt(priceStr, 10)
        if (!isNaN(price) && price > 0) {
          const cleanModel = model.toUpperCase()
          prices[cleanModel] = price
        }
      }
    }
  }

  return prices
}

export async function GET(request: Request) {
  const ip = request.headers.get('x-forwarded-for') || 'unknown'
  
  if (!checkRateLimit(ip)) {
    return NextResponse.json(
      { error: 'Çok fazla istek. Lütfen biraz bekleyin.' },
      { status: 429 }
    )
  }
  
  try {
    if (cache && Date.now() - cache.timestamp < CACHE_DURATION) {
      return NextResponse.json(cache.prices)
    }

    const prices = await fetchPricesFromSheet()
    
    cache = {
      prices,
      timestamp: Date.now()
    }

    return NextResponse.json(prices)
  } catch (error) {
    console.error('Error fetching prices:', error)
    return NextResponse.json(
      { error: 'Fiyatlar yüklenirken hata oluştu' },
      { status: 500 }
    )
  }
}
