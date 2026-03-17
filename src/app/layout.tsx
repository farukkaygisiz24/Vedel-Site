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
  return (
    <html lang="tr">
      <head>
        {/* Google Tag (gtag.js) - Next.js Script bileşeni ile güvenli yükleme */}
        <Script
          src="https://www.googletagmanager.com/gtag/js?id=AW-999471423"
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
      </head>
      <body className={`${inter.variable} antialiased`}>
        <Header />
        <main>{children}</main>
        <Footer />
      </body>
    </html>
  );
}
