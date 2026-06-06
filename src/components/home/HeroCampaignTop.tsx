import { CAMPAIGN_HERO_IMAGE, CAMPAIGN_HERO_VIDEO } from '@/config/campaign'
import HeroTop from './HeroTop'

export default function HeroCampaignTop() {
  return (
    <HeroTop
      backgroundSrc={CAMPAIGN_HERO_IMAGE}
      backgroundVideoSrc={CAMPAIGN_HERO_VIDEO}
      backgroundPosterSrc={CAMPAIGN_HERO_IMAGE}
      backgroundAlt="MHI Yaz Kampanyası — 8 Yıl Garanti, 2500 TL MaxiPuan, 12 Ay Taksit"
      backgroundClassName="object-contain object-center"
      backgroundVideoClassName="object-contain object-center"
      backgroundFitContain
      overlayClassName="bg-transparent pointer-events-none"
      showPattern={false}
      showDecorativeBlobs={false}
      hideLeadContent
      hideCategoryGrid
    />
  )
}
