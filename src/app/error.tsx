'use client'

import { useEffect } from 'react'
import Link from 'next/link'
import { Home, RefreshCw, AlertTriangle } from 'lucide-react'

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error('Application error:', error)
  }, [error])

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100 flex items-center justify-center p-4">
      <div className="max-w-lg w-full text-center">
        <div className="relative mb-8 flex justify-center">
          <div className="relative">
            <div className="w-24 h-24 bg-gradient-to-br from-red-500 to-orange-500 rounded-full flex items-center justify-center shadow-xl">
              <AlertTriangle className="w-12 h-12 text-white" />
            </div>
            <div className="absolute -top-2 -right-2 w-8 h-8 bg-red-600 rounded-full flex items-center justify-center text-white text-sm font-bold">
              !
            </div>
          </div>
        </div>

        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Bir Hata Oluştu
        </h1>

        <p className="text-gray-600 mb-8 text-lg">
          Üzgünüz, bir şeyler yanlış gitti. Sayfayı yenilemeyi deneyebilir veya ana sayfaya dönebilirsiniz.
        </p>

        {error?.digest && (
          <p className="text-sm text-gray-400 mb-6 font-mono">
            Hata kodu: {error.digest}
          </p>
        )}

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button
            onClick={reset}
            className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-teal-600 to-emerald-600 text-white font-semibold rounded-lg hover:from-teal-700 hover:to-emerald-700 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
          >
            <RefreshCw className="w-5 h-5" />
            Yeniden Dene
          </button>

          <Link
            href="/"
            className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-white text-gray-700 font-semibold rounded-lg border-2 border-gray-200 hover:border-teal-500 hover:text-teal-600 transition-all duration-200"
          >
            <Home className="w-5 h-5" />
            Ana Sayfa
          </Link>
        </div>

        <div className="mt-12 p-4 bg-white/50 rounded-lg backdrop-blur-sm">
          <p className="text-sm text-gray-500">
            Yardıma ihtiyacınız varsa{' '}
            <Link href="/iletisim" className="text-teal-600 hover:underline font-medium">
              iletişim
            </Link>
            {' '}sayfamızdan bize ulaşabilirsiniz.
          </p>
        </div>
      </div>
    </div>
  )
}
