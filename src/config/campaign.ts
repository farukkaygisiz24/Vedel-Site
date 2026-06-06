/**
 * Kampanya hero anahtarı.
 *
 * Aktif:  CAMPAIGN_HERO_ENABLED = true  (varsayılan)
 * Kapat:  false yapın veya NEXT_PUBLIC_CAMPAIGN=off
 *
 * Video: public/campaign/mhi-yaz-kampanya.mp4
 */
const campaignExplicitlyOff = process.env.NEXT_PUBLIC_CAMPAIGN === 'off'

export const CAMPAIGN_HERO_ENABLED = !campaignExplicitlyOff

export const CAMPAIGN_HERO_IMAGE = '/campaign/mhi-yaz-kampanya.png'
export const CAMPAIGN_HERO_VIDEO = '/campaign/mhi-yaz-kampanya.mp4'

/** Kampanya banner/video teması — yan boşluklar ve hero zemin rengi */
export const CAMPAIGN_SURFACE_CLASS = 'bg-[#f4efe6]'
