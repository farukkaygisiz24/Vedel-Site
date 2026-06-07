import { GOOGLE_ADS_PHONE_CONVERSION_SEND_TO } from '@/config/analytics'
import { hasMarketingConsent } from '@/lib/cookieConsent'

declare global {
  interface Window {
    gtag?: (...args: unknown[]) => void
  }
}

export function trackPhoneClick(phoneNumber?: string) {
  if (!hasMarketingConsent()) return
  if (typeof window.gtag !== 'function') return

  window.gtag('event', 'conversion', {
    send_to: GOOGLE_ADS_PHONE_CONVERSION_SEND_TO,
  })

  window.gtag('event', 'phone_click', {
    event_category: 'contact',
    event_label: phoneNumber ?? 'phone',
  })
}
