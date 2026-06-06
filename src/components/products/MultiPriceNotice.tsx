import { Info } from 'lucide-react'

export default function MultiPriceNotice({ className = '' }: { className?: string }) {
  return (
    <div
      className={`flex items-start gap-3 rounded-xl border border-blue-200 bg-blue-50 px-4 py-3.5 sm:px-5 sm:py-4 ${className}`}
      role="note"
    >
      <Info className="mt-0.5 h-5 w-5 shrink-0 text-blue-600" aria-hidden="true" />
      <p className="text-sm leading-relaxed text-blue-900 sm:text-[0.9375rem]">
        Fiyatlar cihazlar için adet fiyatlarıdır. Her cihaz ayrı fiyatlandırılır. Montaj detayları
        için lütfen bizi arayınız.
      </p>
    </div>
  )
}
