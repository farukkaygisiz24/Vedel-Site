'use client'

import Image from 'next/image'
import Link from 'next/link'
import { ArrowRight } from 'lucide-react'
import { brandCategories } from './heroData'

type HeroBrandCardsProps = {
  variant?: 'dark' | 'light'
  className?: string
}

export default function HeroBrandCards({ variant = 'dark', className = '' }: HeroBrandCardsProps) {
  const light = variant === 'light'

  return (
    <div className={className}>
      {brandCategories.map((category, index) => (
        <Link
          key={index}
          href={category.href}
          className={
            light
              ? 'group flex items-stretch gap-0 overflow-hidden rounded-2xl border border-gray-200/90 bg-white shadow-sm transition-all duration-300 hover:-translate-y-0.5 hover:border-gray-300 hover:shadow-lg'
              : 'group flex items-stretch gap-0 overflow-hidden rounded-2xl border border-white/15 bg-white/10 backdrop-blur-md transition-all duration-300 hover:-translate-y-0.5 hover:border-white/30 hover:bg-white/15 hover:shadow-xl hover:shadow-cyan-500/10'
          }
        >
          <div className="relative w-32 shrink-0 bg-white p-3 sm:w-36">
            <div className="relative h-full min-h-[88px] w-full">
              <Image
                src={category.image}
                alt={category.name}
                fill
                sizes="144px"
                className="object-contain transition-transform duration-500 group-hover:scale-105"
              />
            </div>
          </div>

          <div className="flex flex-1 items-center justify-between gap-4 px-4 py-4 sm:px-5">
            <div className="min-w-0">
              <div className="mb-2.5 flex h-9 w-full max-w-48 items-center justify-center rounded-lg bg-white px-3 py-1.5">
                <Image
                  src={category.logo}
                  alt={category.name}
                  width={160}
                  height={48}
                  className="h-6 max-w-full w-auto object-contain"
                  style={{ width: 'auto' }}
                />
              </div>
              <h3 className={`text-base font-bold ${light ? 'text-gray-900' : 'text-white'}`}>
                {category.name}
              </h3>
              <p className={`text-sm ${light ? 'text-gray-600' : 'text-blue-200/90'}`}>
                {category.desc}
              </p>
            </div>

            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-red-600 text-white transition-all duration-300 group-hover:scale-110 group-hover:bg-red-500">
              <ArrowRight className="h-5 w-5 transition-transform group-hover:translate-x-0.5" />
            </div>
          </div>
        </Link>
      ))}
    </div>
  )
}
