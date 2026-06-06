import { Metadata } from 'next'
import KlimaSecWizard from '@/components/KlimaSecWizard'

export const metadata: Metadata = {
    title: 'Klimanı Seç | Vedel Klima',
    description: 'Odanıza en uygun klimayı hesaplayın. BTU kapasite hesaplayıcı ile ihtiyacınıza özel klima önerileri alın.',
    keywords: ['klima seçimi', 'btu hesaplama', 'klima kapasite hesaplama', 'oda klima hesabı'],
    openGraph: {
        type: 'website',
        locale: 'tr_TR',
        url: 'https://vedel.com.tr/klimani-sec',
        siteName: 'VEDEL Klima',
        title: 'Klimanı Seç | VEDEL Klima',
        description: 'Odanıza en uygun klimayı hesaplayın. BTU kapasite hesaplayıcı ile ihtiyacınıza özel klima önerileri alın.',
        images: [
            {
                url: '/vedel-logo.png',
                width: 1200,
                height: 630,
                alt: 'VEDEL Klima - Klimanı Seç',
            },
        ],
    },
    twitter: {
        card: 'summary_large_image',
        title: 'Klimanı Seç | VEDEL Klima',
        description: 'Odanıza en uygun klimayı hesaplayın. BTU kapasite hesaplayıcı.',
        images: ['/vedel-logo.png'],
    },
}

export default function KlimaSecPage() {
    return <KlimaSecWizard />
}
