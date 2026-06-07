export const SITE_NAME = 'VEDEL Klima'

/**
 * Tarayıcı sekmesi için kısa başlık.
 * layout.tsx içindeki template otomatik olarak `| VEDEL Klima` ekler.
 */
export function tabTitle(shortTitle: string): string {
  return shortTitle
}

/** Open Graph / Twitter / paylaşım kartları için tam başlık */
export function fullTitle(shortTitle: string): string {
  return `${shortTitle} | ${SITE_NAME}`
}

/** layout.tsx default başlığı (template uygulanmaz) */
export const DEFAULT_TAB_TITLE =
  'Bursa Mitsubishi Heavy Industries Yetkili Bayi | Vedel Klima'
