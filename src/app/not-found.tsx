import Link from 'next/link'
import { Home, ArrowLeft, Search } from 'lucide-react'

export default function NotFound() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100 flex items-center justify-center p-4">
      <div className="max-w-lg w-full text-center">
        <div className="relative mb-8">
          <div className="text-[100px] sm:text-[180px] font-bold text-gray-200 leading-none select-none">
            404
          </div>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-24 h-24 bg-gradient-to-br from-teal-500 to-emerald-500 rounded-full flex items-center justify-center shadow-xl">
              <Search className="w-12 h-12 text-white" />
            </div>
          </div>
        </div>

        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Sayfa Bulunamadı
        </h1>

        <p className="text-gray-600 mb-8 text-lg">
          Aradığınız sayfa bulunamadı veya taşınmış olabilir.
          Ana sayfaya dönebilir veya ürünlerimizi inceleyebilirsiniz.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/"
            className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-teal-600 to-emerald-600 text-white font-semibold rounded-lg hover:from-teal-700 hover:to-emerald-700 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
          >
            <Home className="w-5 h-5" />
            Ana Sayfa
          </Link>

          <Link
            href="/urunler/splitsistemler"
            className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-white text-gray-700 font-semibold rounded-lg border-2 border-gray-200 hover:border-teal-500 hover:text-teal-600 transition-all duration-200"
          >
            <ArrowLeft className="w-5 h-5" />
            Ürünler
          </Link>
        </div>

        <div className="mt-12 grid grid-cols-2 sm:grid-cols-4 gap-4">
          <Link
            href="/hakkimizda"
            className="p-4 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow"
          >
            <p className="font-medium text-gray-900">Hakkımızda</p>
            <p className="text-sm text-gray-500">Biz kimiz?</p>
          </Link>
          <Link
            href="/iletisim"
            className="p-4 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow"
          >
            <p className="font-medium text-gray-900">İletişim</p>
            <p className="text-sm text-gray-500">Bize ulaşın</p>
          </Link>
          <Link
            href="/klimani-sec"
            className="p-4 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow"
          >
            <p className="font-medium text-gray-900">Klimanı Seç</p>
            <p className="text-sm text-gray-500">BTU hesapla</p>
          </Link>
          <Link
            href="/urunler/splitsistemler"
            className="p-4 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow"
          >
            <p className="font-medium text-gray-900">Ürünler</p>
            <p className="text-sm text-gray-500">Tüm klimalar</p>
          </Link>
        </div>
      </div>
    </div>
  )
}
