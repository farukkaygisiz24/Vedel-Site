import { join } from 'path'

export const CAMPAIGN_VIDEO_FILENAME = 'mhi-yaz-kampanya.mp4'

export const CAMPAIGN_VIDEO_PATH = join(
  process.cwd(),
  'private',
  'campaign',
  CAMPAIGN_VIDEO_FILENAME
)

export const CAMPAIGN_VIDEO_API_PATH = '/api/campaign/video'

// İzin verilen origin'leri tam eşleşmeyle kontrol et (subdomain dahil)
const ALLOWED_ORIGIN_RE = /^https?:\/\/(?:[a-z0-9-]+\.)*vedel\.com\.tr(?::\d+)?$/i
const ALLOWED_HOST_RE = /^(?:[a-z0-9-]+\.)*vedel\.com\.tr(?::\d+)?$/i
const DEV_RE = /^https?:\/\/localhost(?::\d+)?$/i

/** Sadece site üzerinden gelen isteklere izin ver (doğrudan link / hotlink engeli) */
export function isAllowedVideoRequest(referer: string | null, origin: string | null, host: string | null): boolean {
  if (process.env.NODE_ENV === 'development') return true

  // Origin header ile tam eşleşme kontrolü
  if (origin && (ALLOWED_ORIGIN_RE.test(origin) || DEV_RE.test(origin))) return true

  // Referer header — URL'den sadece origin kısmını al
  if (referer) {
    try {
      const refOrigin = new URL(referer).origin
      if (ALLOWED_ORIGIN_RE.test(refOrigin) || DEV_RE.test(refOrigin)) return true
    } catch {
      // Geçersiz URL ise geç
    }
  }

  // Host header — kendi sunucudan gelen istekler
  if (host && ALLOWED_HOST_RE.test(host)) return true

  return false
}
