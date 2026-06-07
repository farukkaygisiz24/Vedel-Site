import { join } from 'path'

export const CAMPAIGN_VIDEO_FILENAME = 'mhi-yaz-kampanya.mp4'

export const CAMPAIGN_VIDEO_PATH = join(
  process.cwd(),
  'private',
  'campaign',
  CAMPAIGN_VIDEO_FILENAME
)

export const CAMPAIGN_VIDEO_API_PATH = '/api/campaign/video'

/** Sadece site üzerinden gelen isteklere izin ver (doğrudan link / hotlink engeli) */
export function isAllowedVideoRequest(referer: string | null, origin: string | null, host: string | null): boolean {
  if (process.env.NODE_ENV === 'development') return true

  const candidates = [referer ?? '', origin ?? '', host ?? ''].join(' ').toLowerCase()

  return (
    candidates.includes('vedel.com.tr') ||
    candidates.includes('localhost') ||
    candidates.includes('127.0.0.1') ||
    candidates.includes('vercel.app')
  )
}
