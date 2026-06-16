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

/** Kampanya hero üst bandı — sıcak krem; ürün kartları ve kırmızı CTA ile uyumlu */
export const CAMPAIGN_SURFACE_CLASS = 'bg-[#f6f0e8]'

/** Kampanya "Neden Vedel?" bölümü — hafif mavi-gri; mavi rozet ve kart aksanlarıyla uyumlu */
export const CAMPAIGN_CONTENT_SURFACE_CLASS = 'bg-[#f0f4f8]'

/** Kampanya içerik bölümü üst sınırı — CAMPAIGN_CONTENT_SURFACE_CLASS ile eşleşir */
export const CAMPAIGN_CONTENT_BORDER_CLASS = 'border-[#dde4ec]'
