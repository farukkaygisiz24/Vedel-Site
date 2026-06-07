export const COOKIE_CONSENT_KEY = 'vedel_cookie_consent'

export type CookieConsentChoice = 'accepted' | 'rejected'

export function getCookieConsent(): CookieConsentChoice | null {
  if (typeof window === 'undefined') return null

  const value = localStorage.getItem(COOKIE_CONSENT_KEY)
  if (value === 'accepted' || value === 'rejected') return value
  return null
}

export function setCookieConsent(choice: CookieConsentChoice): void {
  localStorage.setItem(COOKIE_CONSENT_KEY, choice)
  window.dispatchEvent(new CustomEvent('vedel-cookie-consent', { detail: choice }))
}

export function hasMarketingConsent(): boolean {
  return getCookieConsent() === 'accepted'
}
