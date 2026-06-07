'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { Cookie, X } from 'lucide-react'
import {
  COOKIE_CONSENT_KEY,
  getCookieConsent,
  setCookieConsent,
  type CookieConsentChoice,
} from '@/lib/cookieConsent'
import { activateGoogleAdsTracking } from '@/lib/googleTag'

export default function CookieConsent() {
  const [choice, setChoice] = useState<CookieConsentChoice | null>(null)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    const stored = getCookieConsent()
    setChoice(stored)
    setMounted(true)

    if (stored === 'accepted') {
      activateGoogleAdsTracking()
    }

    const onStorage = (event: StorageEvent) => {
      if (event.key === COOKIE_CONSENT_KEY) {
        setChoice(getCookieConsent())
      }
    }

    const onConsent = (event: Event) => {
      const detail = (event as CustomEvent<CookieConsentChoice>).detail
      setChoice(detail)
    }

    window.addEventListener('storage', onStorage)
    window.addEventListener('vedel-cookie-consent', onConsent)

    return () => {
      window.removeEventListener('storage', onStorage)
      window.removeEventListener('vedel-cookie-consent', onConsent)
    }
  }, [])

  const saveChoice = (next: CookieConsentChoice) => {
    setCookieConsent(next)
    setChoice(next)
    if (next === 'accepted') {
      activateGoogleAdsTracking()
    }
  }

  const showBanner = mounted && choice === null

  return (
    <>
      {showBanner && (
        <div
          className="fixed inset-x-0 bottom-0 z-[100] p-4 sm:p-5"
          role="dialog"
          aria-labelledby="cookie-consent-title"
          aria-describedby="cookie-consent-desc"
        >
          <div className="relative mx-auto flex max-w-4xl flex-col gap-4 rounded-2xl border border-gray-200 bg-white p-4 shadow-2xl sm:flex-row sm:items-center sm:gap-6 sm:p-5">
            <div className="flex min-w-0 flex-1 items-start gap-3">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-red-50">
                <Cookie className="h-5 w-5 text-red-600" aria-hidden="true" />
              </div>
              <div className="min-w-0">
                <p id="cookie-consent-title" className="text-sm font-bold text-gray-900 sm:text-base">
                  Çerez Kullanımı
                </p>
                <p id="cookie-consent-desc" className="mt-1 text-xs leading-relaxed text-gray-600 sm:text-sm">
                  Deneyiminizi iyileştirmek ve reklam performansını ölçmek için çerezler kullanıyoruz.
                  Zorunlu çerezler site işlevselliği için gereklidir. Detaylar için{' '}
                  <Link href="/cerez-politikasi" className="font-medium text-red-600 hover:underline">
                    Çerez Politikası
                  </Link>{' '}
                  ve{' '}
                  <Link href="/gizlilik-politikasi" className="font-medium text-red-600 hover:underline">
                    Gizlilik Politikası
                  </Link>{' '}
                  sayfalarımıza bakabilirsiniz.
                </p>
              </div>
            </div>

            <div className="flex shrink-0 flex-col gap-2 sm:flex-row sm:items-center">
              <button
                type="button"
                onClick={() => saveChoice('rejected')}
                className="min-h-10 rounded-xl border border-gray-200 px-4 py-2 text-sm font-semibold text-gray-700 transition-colors hover:bg-gray-50"
              >
                Reddet
              </button>
              <button
                type="button"
                onClick={() => saveChoice('accepted')}
                className="min-h-10 rounded-xl bg-red-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-red-700"
              >
                Kabul Et
              </button>
            </div>

            <button
              type="button"
              onClick={() => saveChoice('rejected')}
              className="absolute right-6 top-4 rounded-lg p-1 text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600 sm:hidden"
              aria-label="Kapat"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}
    </>
  )
}
