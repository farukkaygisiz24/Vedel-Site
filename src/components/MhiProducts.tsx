'use client'

import { useState, useMemo } from 'react'
import {
  ListingProduct,
  ProductListingLayout,
  ProductCategorySection,
  PromoBanner,
} from '@/components/products/shared'

interface MhiSplitData {
  brand: string
  logo: string
  description: string
  split: {
    trend: ListingProduct[]
    plus: ListingProduct[]
    diamond: ListingProduct[]
    diamond_titanyum: ListingProduct[]
    yuksek_kapasite: ListingProduct[]
  }
}

export default function MhiProductsClient({ data }: { data: MhiSplitData }) {
  const allProducts = useMemo(() => {
    const products: ListingProduct[] = []
    if (data.split.trend) products.push(...data.split.trend)
    if (data.split.plus) products.push(...data.split.plus)
    if (data.split.diamond) products.push(...data.split.diamond)
    if (data.split.diamond_titanyum) products.push(...data.split.diamond_titanyum)
    if (data.split.yuksek_kapasite) products.push(...data.split.yuksek_kapasite)
    return products
  }, [data])

  const [filteredProducts, setFilteredProducts] = useState<ListingProduct[]>(allProducts)

  const series = [
    { key: 'trend', title: 'Trend Serisi', desc: 'Ekonomik çözüm', products: data.split.trend || [] },
    { key: 'plus', title: 'Plus Serisi', desc: 'Konfor ve tasarruf', products: data.split.plus || [] },
    { key: 'diamond', title: 'Diamond Serisi', desc: 'Premium performans', products: data.split.diamond || [] },
    { key: 'diamond_titanyum', title: 'Diamond Titanyum Serisi', desc: 'Premium titanyum tasarım', products: data.split.diamond_titanyum || [] },
    { key: 'yuksek_kapasite', title: 'Yüksek Kapasite Serisi', desc: 'Yüksek kapasiteli çözümler', products: data.split.yuksek_kapasite || [] },
  ]

  return (
    <ProductListingLayout
      allProducts={allProducts}
      filteredProducts={filteredProducts}
      onFilterChange={setFilteredProducts}
      brand="mhi"
      accent="red"
      banner={
        <PromoBanner
          accent="red"
          title="Hangi Klimayı Seçeceğinize Karar Veremediniz mi?"
          description="Klimanızı seçmenizde size yardımcı olalım! İhtiyacınıza en uygun klimayı birlikte bulalım."
          href="/klimani-sec"
          buttonLabel="Klimanı Seç"
        />
      }
    >
      {series.map(({ key, title, desc, products: serieProducts }) => {
        const filteredSerieProducts = filteredProducts.filter(p =>
          serieProducts.some(sp => sp.id === p.id)
        )

        return (
          <ProductCategorySection
            key={key}
            title={title}
            desc={desc}
            products={filteredSerieProducts}
            brand="mhi"
            accent="red"
          />
        )
      })}
    </ProductListingLayout>
  )
}
