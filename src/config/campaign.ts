/**
 * Kampanya hero anahtarı.
 *
 * Aktif:  varsayılan (açık)
 * Kapat:  NEXT_PUBLIC_CAMPAIGN=off
 *
 * Video: private/campaign/ (API üzerinden stream)
 * Poster: public/campaign/mhi-yaz-kampanya.png
 */
const campaignExplicitlyOff = process.env.NEXT_PUBLIC_CAMPAIGN === 'off'

export const CAMPAIGN_HERO_ENABLED = !campaignExplicitlyOff

export const CAMPAIGN_HERO_IMAGE = '/campaign/mhi-yaz-kampanya.png'
export const CAMPAIGN_HERO_VIDEO = '/api/campaign/video'

/** Kampanya banner/video teması — yan boşluklar ve hero zemin rengi */
export const CAMPAIGN_SURFACE_CLASS = 'bg-[#f4efe6]'
