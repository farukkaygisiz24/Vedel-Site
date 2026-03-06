'use client'

import Link from 'next/link'
import Image from 'next/image'
import { Phone, Mail, MapPin, ArrowRight } from 'lucide-react'

export default function Footer() {
  return (
    <footer className="bg-white">
      <div className="container mx-auto px-4 py-16">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
          <div>
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-gray-100 rounded-xl p-1 relative">
                <Image
                  src="/vedel-logo.png"
                  alt="Vedel"
                  fill
                  className="object-contain"
                />
              </div>
              <span className="text-gray-900 font-bold text-xl">Vedel</span>
            </div>
            <p className="text-gray-600 text-sm leading-relaxed mb-6">
              Mitsubishi Heavy Industries ve Euroform yetkili bayisi olarak iklimlendirme ihtiyaçlarınızda profesyonel çözümler sunuyoruz.
            </p>
            <div className="flex items-center gap-2 text-gray-600 text-sm">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
              <span>Yetkili Satış ve Servis Bayi</span>
            </div>
            <div className="flex items-center gap-2 text-gray-600 text-sm mt-2">
              <span className="w-2 h-2 bg-gray-400 rounded-full"></span>
              <span>Bakım ve Onarım Hizmetleri</span>
            </div>
          </div>

          <div>
            <h3 className="text-gray-900 font-bold text-lg mb-6">Hızlı Linkler</h3>
            <ul className="space-y-3">
              {[
                { name: 'Ana Sayfa', href: '/' },
                { name: 'Klimalar', href: '/klimani-sec' },
                { name: 'Hakkımızda', href: '/hakkimizda' },
                { name: 'İletişim', href: '/iletisim' },
              ].map((link) => (
                <li key={link.name}>
                  <Link
                    href={link.href}
                    className="text-gray-600 hover:text-orange-500 transition-colors flex items-center gap-2 group"
                  >
                    <ArrowRight className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity text-orange-500" />
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="text-gray-900 font-bold text-lg mb-6">İletişim</h3>
            <ul className="space-y-4">
              <li className="flex items-start gap-3">
                <Phone className="w-5 h-5 text-orange-500 flex-shrink-0 mt-0.5" />
                <div>
                  <a href="tel:+902244132316" className="text-gray-700 hover:text-gray-900 transition-colors">
                    +90 224 413 16 17
                  </a>
                </div>
              </li>
              <li className="flex items-start gap-3">
                <Mail className="w-5 h-5 text-orange-500 flex-shrink-0 mt-0.5" />
                <div>
                  <a href="mailto:vedel@vedel.com.tr" className="text-gray-700 hover:text-gray-900 transition-colors">
                    vedel@vedel.com.tr
                  </a>
                </div>
              </li>
              <li className="flex items-start gap-3">
                <MapPin className="w-5 h-5 text-orange-500 flex-shrink-0 mt-0.5" />
                <div className="text-gray-600 space-y-2 text-sm break-words">
                  <p className="font-semibold text-gray-800">Kayapa Bayi</p>
                  <p>30 Ağustos Zafer Mah. Bozyaka Cad. NO:11/CA Nilüfer / Bursa</p>
                  <p className="font-semibold text-gray-800 mt-3">Özlüce Bayi</p>
                  <p>Altınşehir Mah. Uğur Mumcu BLV. NO:58/E Nilüfer Bursa</p>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <div className="border-t border-gray-200">
        <div className="container mx-auto px-4 py-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-gray-500 text-sm">
              © {new Date().getFullYear()} Vedel İklimlendirme. Tüm hakları saklıdır.
            </p>
            <a
              href="mailto:farukkaygisiz24@gmail.com"
              className="text-gray-400 text-sm hover:text-gray-600 transition-colors"
            >
              Build by farukkaygisiz24
            </a>
          </div>
        </div>
      </div>
    </footer>
  )
}
