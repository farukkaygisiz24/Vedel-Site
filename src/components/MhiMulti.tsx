'use client'

import { useState, useMemo } from 'react'
import {
  ListingProduct,
  ProductListingLayout,
  ProductCategorySection,
  PromoBanner,
} from '@/components/products/shared'

interface MhiMultiData {
  brand: string
  logo: string
  description: string
  categories: {
    outdoor: ListingProduct[]
    indoor_wall: ListingProduct[]
    cassette: ListingProduct[]
    ducted: ListingProduct[]
  }
}

export default function MhiMultiClient({ data }: { data: MhiMultiData }) {
  const allProducts = useMemo(() => {
    const products: ListingProduct[] = []
    if (data.categories.outdoor) products.push(...data.categories.outdoor)
    if (data.categories.indoor_wall) products.push(...data.categories.indoor_wall)
    if (data.categories.cassette) products.push(...data.categories.cassette)
    if (data.categories.ducted) products.push(...data.categories.ducted)
    return products
  }, [data])

  const [filteredProducts, setFilteredProducts] = useState<ListingProduct[]>(allProducts)

  const categories = [
    { key: 'outdoor', title: 'Dış Üniteler', desc: 'Tek dış üniteye birden fazla iç ünite bağlayın', products: data.categories.outdoor || [] },
    { key: 'indoor_wall', title: 'Duvar Tipi İç Üniteler', desc: 'Klasik duvar tipi iç üniteler', products: data.categories.indoor_wall || [] },
    { key: 'cassette', title: 'Kaset Tipi İç Üniteler', desc: 'Tavana montaj 4 yöne üflemeli kaset tipi üniteler', products: data.categories.cassette || [] },
    { key: 'ducted', title: 'Kanal Tipi İç Üniteler', desc: 'Gizli montaj kanal tipi üniteler', products: data.categories.ducted || [] },
  ]

  return (
    <ProductListingLayout
      allProducts={allProducts}
      filteredProducts={filteredProducts}
      onFilterChange={setFilteredProducts}
      brand="mhi_multi"
      accent="red"
      ctaDescription="Uzman ekibimiz ihtiyaçlarınızı analiz ederek en uygun multi klima çözümünü sunmaktadır."
      banner={
        <PromoBanner
          accent="blue"
          title="Multi Klima Seçiminde Zorlanıyor musunuz?"
          description="İç ünitelerinizi seçin, size uygun dış üniteyi ve fiyatı otomatik hesaplayalım!"
          href="/urunler/multisistemler/mhi/hesaplayici"
          buttonLabel="Hesaplayıcıya Git"
        />
      }
    >
      {categories.map(({ key, title, desc, products: categoryProducts }) => {
        const filteredCategoryProducts = filteredProducts.filter(p =>
          categoryProducts.some(cp => cp.id === p.id)
        )

        return (
          <ProductCategorySection
            key={key}
            title={title}
            desc={desc}
            products={filteredCategoryProducts}
            brand="mhi_multi"
            accent="red"
          />
        )
      })}
    </ProductListingLayout>
  )
}
