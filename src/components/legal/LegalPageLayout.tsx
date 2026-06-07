import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'
import type { ReactNode } from 'react'

type LegalSection = {
  title: string
  content: ReactNode
}

type LegalPageLayoutProps = {
  title: string
  subtitle: string
  lastUpdated: string
  sections: LegalSection[]
}

export default function LegalPageLayout({
  title,
  subtitle,
  lastUpdated,
  sections,
}: LegalPageLayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      <section className="relative overflow-hidden pt-20 pb-12 sm:pb-16">
        <div className="absolute inset-0 bg-gradient-to-br from-red-900 via-red-800 to-red-900" />
        <div className="absolute inset-0 opacity-10">
          <div className="absolute left-4 top-20 h-48 w-48 rounded-full bg-white blur-3xl sm:left-10 sm:h-72 sm:w-72" />
          <div className="absolute bottom-6 right-4 h-56 w-56 rounded-full bg-red-400 blur-3xl sm:bottom-10 sm:right-20 sm:h-96 sm:w-96" />
        </div>

        <div className="container relative z-10 mx-auto px-4 sm:px-6">
          <Link
            href="/"
            className="mb-6 inline-flex items-center gap-2 text-sm text-red-200 transition-colors hover:text-white"
          >
            <ArrowLeft className="h-4 w-4" />
            Ana Sayfa
          </Link>
          <div className="mx-auto max-w-3xl">
            <h1 className="mb-4 text-3xl font-bold text-white sm:text-4xl md:text-5xl">
              {title}
            </h1>
            <p className="text-base leading-relaxed text-red-100 sm:text-lg">
              {subtitle}
            </p>
            <p className="mt-4 text-sm text-red-200/80">Son güncelleme: {lastUpdated}</p>
          </div>
        </div>
      </section>

      <section className="py-10 sm:py-14 md:py-16">
        <div className="container mx-auto px-4 sm:px-6">
          <article className="mx-auto max-w-3xl rounded-2xl border border-gray-100 bg-white p-6 shadow-sm sm:p-8 md:p-10">
            <div className="prose prose-gray max-w-none prose-headings:text-gray-900 prose-p:text-gray-600 prose-li:text-gray-600 prose-a:text-red-600 prose-a:no-underline hover:prose-a:underline">
              {sections.map((section) => (
                <section key={section.title} className="mb-8 last:mb-0">
                  <h2 className="mb-3 text-xl font-bold text-gray-900 sm:text-2xl">
                    {section.title}
                  </h2>
                  <div className="space-y-3 text-sm leading-relaxed text-gray-600 sm:text-base">
                    {section.content}
                  </div>
                </section>
              ))}
            </div>

            <div className="mt-10 border-t border-gray-100 pt-6 text-sm text-gray-500">
              <p>
                Sorularınız için{' '}
                <a href="mailto:vedel@vedel.com.tr" className="font-medium text-red-600 hover:underline">
                  vedel@vedel.com.tr
                </a>{' '}
                adresine yazabilir veya{' '}
                <Link href="/iletisim" className="font-medium text-red-600 hover:underline">
                  iletişim
                </Link>{' '}
                sayfamızdan bize ulaşabilirsiniz.
              </p>
            </div>
          </article>
        </div>
      </section>
    </div>
  )
}
