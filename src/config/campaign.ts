/**
 * Kampanya hero anahtarı.
 *
 * Kapalı: varsayılan
 * Açmak:  NEXT_PUBLIC_CAMPAIGN=on  veya aşağıdaki sabiti true yap
 *
 * Video: private/campaign/ (API üzerinden stream)
 * Poster: public/campaign/mhi-yaz-kampanya.png
 */
export const CAMPAIGN_HERO_ENABLED =
  process.env.NEXT_PUBLIC_CAMPAIGN === 'on' ? true : false

export const CAMPAIGN_HERO_IMAGE = '/campaign/mhi-yaz-kampanya.png'
export const CAMPAIGN_HERO_VIDEO = '/api/campaign/video'

/** Kampanya hero üst bandı — sıcak krem; ürün kartları ve kırmızı CTA ile uyumlu */
export const CAMPAIGN_SURFACE_CLASS = 'bg-[#f6f0e8]'

/** Kampanya "Neden Vedel?" bölümü — hafif mavi-gri; mavi rozet ve kart aksanlarıyla uyumlu */
export const CAMPAIGN_CONTENT_SURFACE_CLASS = 'bg-[#f0f4f8]'

/** Kampanya içerik bölümü üst sınırı — CAMPAIGN_CONTENT_SURFACE_CLASS ile eşleşir */
export const CAMPAIGN_CONTENT_BORDER_CLASS = 'border-[#dde4ec]'
