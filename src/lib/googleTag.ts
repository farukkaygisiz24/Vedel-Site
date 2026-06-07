import {
  GOOGLE_ADS_ID,
  GOOGLE_ADS_PHONE_CONVERSION_NUMBER,
  GOOGLE_ADS_PHONE_CONVERSION_SEND_TO,
} from '@/config/analytics'

declare global {
  interface Window {
    gtag?: (...args: unknown[]) => void
    dataLayer?: unknown[]
  }
}

/** Çerez kabul edildiğinde telefon dönüşüm takibini etkinleştirir. */
export function activateGoogleAdsTracking() {
  if (typeof window.gtag !== 'function') return

  window.gtag('consent', 'update', {
    ad_storage: 'granted',
    analytics_storage: 'granted',
    ad_user_data: 'granted',
    ad_personalization: 'granted',
  })

  window.gtag('config', GOOGLE_ADS_PHONE_CONVERSION_SEND_TO, {
    phone_conversion_number: GOOGLE_ADS_PHONE_CONVERSION_NUMBER,
  })
}

export { GOOGLE_ADS_ID }
