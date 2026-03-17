import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import Script from "next/script"; // Script bileşenini ekledik

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
};

export const metadata: Metadata = {
  metadataBase: new URL('https://vedel.com.tr'),
  title: {
    default: "Bursa Mitsubishi Heavy Industries Yetkili Bayi | Vedel Klima",
    template: "%s | VEDEL Klima",
  },
  description: "Bursa'da Mitusbishi Heavy Industries ve Euroform klima yetkili satış ve servis noktası. Profesyonel montaj hizmeti, VRF Sistem çözümleri. Hemen teklif alın: (0224) 413 23 16",
  keywords: [
             "klima", 
             "mitsubishi heavy bursa",
             "bursa mitsubishi klima yetkili bayi",
             "vedel klima",
             "vedel klima bursa",
             "mitsubishi klima servis",
             "bursa",
             "özlüce klima bursa",
             "salon tipi klima",
             "kaset tipi klima",
             "klima bakım",
             "klima servis bursa",
             "klima arıza bursa",
             "kayapa klima",
             "mitsubishi kayapa",
             "euroform",
             "euroform bursa",
             "mitsubishi klima fiyatları",
             "ev tipi klima",
             "vrf sistemleri"
             ],
  authors: [{ name: "VEDEL" }],
  icons: {
    icon: "/vedel-logo.png",
    apple: "/vedel-logo.png",
  },
  creator: "VEDEL",
  publisher: "VEDEL",
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  alternates: {
    canonical: "https://vedel.com.tr",
  },
  openGraph: {
    type: "website",
    locale: "tr_TR",
    url: "https://vedel.com.tr",
    siteName: "VEDEL Klima",
    title: "VEDEL - Klima Yetkili Satış ve Bayi",
    description: "VEDEL klima yetkili satış ve bayisi. MHI ve Euroform klimalar, montaj, bakım ve servis hizmetleri.",
    images: [
      {
        url: "/vedel-logo.png",
        width: 1200,
        height: 630,
        alt: "VEDEL Klima",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "VEDEL - Klima Yetkili Satış ve Bayi",
    description: "VEDEL klima yetkili satış ve bayisi. MHI ve Euroform klimalar, montaj, bakım ve servis hizmetleri.",
    images: ["/vedel-logo.png"],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  // İşletme bilgilerini buraya obje olarak tanımlıyoruz
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "LocalBusiness",
    "name": "VEDEL Klima | Bursa Mitsubishi Heavy Yetkili Bayi",
    "image": "https://vedel.com.tr/vedel-logo.png",
    "@id": "https://vedel.com.tr",
    "url": "https://vedel.com.tr",
    "telephone": "+902244132316",
    "address": {
      "@type": "PostalAddress",
      "streetAddress": "Altınşehir Mah. Uğur Mumcu BLV. No:58/E Nilüfer Bursa", // Kral buraya tam adresi yazarsan nokta atışı olur
      "addressLocality": "Bursa",
      "addressRegion": "TR",
      "postalCode": "16130",
      "addressCountry": "TR"
    },
    "openingHoursSpecification": {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
      "opens": "08:30",
      "closes": "18:30"
    },
    "sameAs": [
      "https://www.instagram.com/vedelklima",
      "https://www.facebook.com/profile.php?id=61587239653873&locale=tr_TR"
      ]
  };

  return (
    <html lang="tr">
      <head>
        {/* Google Ads Scriptleri */}
        <Script
          src="https://www.googletagmanager.com/gtag/js?id=AW-18020941072"
          strategy="afterInteractive"
        />
        <Script id="google-ads-tag" strategy="afterInteractive">
          {`
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', 'AW-18020941072');
          `}
        </Script>

        {/* --- İŞTE JSON-LD BURAYA GELİYOR --- */}
        <Script
          id="json-ld"
          type="application/ld+json"
          strategy="afterInteractive"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
      </head>
      <body className={`${inter.variable} antialiased`}>
        <Header />
        <main>{children}</main>
        <Footer />
      </body>
    </html>
  );
}
