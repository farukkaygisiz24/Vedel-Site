'use client'

import { User } from 'lucide-react'
import { getServicePortalUrl } from '@/lib/service-portal'

export default function AccountButton() {
  const href = getServicePortalUrl()

  return (
    <>
      <a
        href={href}
        className="hidden lg:inline-flex items-center gap-2 rounded-md bg-red-600 px-3 py-2 text-sm font-bold text-white transition-colors hover:bg-red-700"
      >
        <User className="h-4 w-4" />
        Giriş
      </a>
      <a
        href={href}
        className="lg:hidden flex h-8 w-8 items-center justify-center rounded-full text-neutral-800 active:bg-gray-100 sm:h-9 sm:w-9 md:h-10 md:w-10 md:hover:bg-gray-100"
        aria-label="Giriş yap"
      >
        <User className="h-5 w-5" />
      </a>
    </>
  )
}
