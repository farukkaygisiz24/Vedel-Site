'use client'

import { useEffect } from 'react'
import { trackPhoneClick } from '@/lib/analytics'
import { getCookieConsent } from '@/lib/cookieConsent'

export default function PhoneClickTracker() {
  useEffect(() => {
    const handleClick = (event: MouseEvent) => {
      if (getCookieConsent() !== 'accepted') return

      const link = (event.target as Element | null)?.closest('a[href^="tel:"]')
      if (!(link instanceof HTMLAnchorElement)) return

      const phoneNumber = link.href.replace(/^tel:/i, '')
      trackPhoneClick(phoneNumber)
    }

    document.addEventListener('click', handleClick, true)
    return () => document.removeEventListener('click', handleClick, true)
  }, [])

  return null
}
