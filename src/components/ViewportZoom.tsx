'use client'

import { useEffect } from 'react'

/** FHD (1920) tasarımı geniş ekranlarda orantılı büyütür; 4K’da küçülmeyi engeller. */
const DESIGN_WIDTH = 1920
const MAX_ZOOM = 1.5

export default function ViewportZoom() {
  useEffect(() => {
    const apply = () => {
      const width = window.innerWidth
      const zoom = Math.max(1, Math.min(width / DESIGN_WIDTH, MAX_ZOOM))
      document.body.style.zoom = zoom === 1 ? '' : String(zoom)
    }

    apply()
    window.addEventListener('resize', apply)
    return () => {
      window.removeEventListener('resize', apply)
      document.body.style.zoom = ''
    }
  }, [])

  return null
}
