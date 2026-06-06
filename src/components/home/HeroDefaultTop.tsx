import HeroTop from './HeroTop'

export default function HeroDefaultTop() {
  return (
    <HeroTop
      backgroundSrc="/sakura.jpg"
      backgroundAlt="Background"
      backgroundClassName="object-cover object-center blur-sm brightness-50"
      overlayClassName="bg-gradient-to-br from-slate-900/70 via-blue-900/50 to-cyan-900/30"
      showPattern
      showDecorativeBlobs
    />
  )
}
