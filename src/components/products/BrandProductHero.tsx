import Image from 'next/image'
import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'

type BrandProductHeroProps = {
  gradientClass: string
  subtitleClass: string
  pageTitle: string
  brandName: string
  logo: string
  description: string
}

export default function BrandProductHero({
  gradientClass,
  subtitleClass,
  pageTitle,
  brandName,
  logo,
  description,
}: BrandProductHeroProps) {
  return (
    <div className={`relative overflow-hidden ${gradientClass} pt-8 pb-5 sm:pt-10 sm:pb-6 md:pt-14 md:pb-8`}>
      <div className="absolute inset-0 bg-black/20" />
      <div className="pointer-events-none absolute inset-0 opacity-10">
        <div className="absolute left-3 top-4 h-14 w-14 rounded-full border border-white sm:left-8 sm:top-6 sm:h-20 sm:w-20" />
        <div className="absolute bottom-4 right-3 h-20 w-20 rounded-full border border-white sm:bottom-6 sm:right-8 sm:h-28 sm:w-28" />
        <div className="absolute left-1/3 top-1/2 hidden h-16 w-16 rounded-full border border-white md:block" />
      </div>

      <div className="container relative z-10 mx-auto px-4 sm:px-6 md:px-8 lg:px-6">
        <Link
          href="/"
          className="mb-3 inline-flex min-h-10 items-center gap-2 text-sm text-white/80 transition-colors active:text-white sm:mb-4"
        >
          <ArrowLeft className="h-4 w-4" />
          Ana Sayfa
        </Link>

        <div className="mb-3 flex flex-col items-start gap-2 sm:mb-4 sm:flex-row sm:items-center sm:gap-4">
          <div className="relative h-16 w-40 shrink-0 rounded-xl bg-white shadow-lg sm:h-[4.5rem] sm:w-48 md:h-20 md:w-56 lg:h-[5.25rem] lg:w-64">
            <div className="absolute inset-x-4 inset-y-2.5 sm:inset-x-5 sm:inset-y-3 md:inset-x-6 lg:inset-x-7">
              <Image
                src={logo}
                alt={brandName}
                fill
                className="object-contain"
                sizes="(max-width: 640px) 160px, 256px"
              />
            </div>
          </div>
          <div className="min-w-0">
            <h1 className="text-xl font-bold text-white sm:text-2xl md:text-3xl lg:text-4xl">
              {pageTitle}
            </h1>
            <p className={`mt-0.5 text-sm sm:text-base ${subtitleClass}`}>{brandName}</p>
          </div>
        </div>

        <p className="max-w-2xl text-sm leading-relaxed text-white/90 sm:text-base">
          {description}
        </p>
      </div>
    </div>
  )
}
