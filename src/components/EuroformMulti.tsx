'use client'

import { useState, useMemo } from 'react'
import {
  ListingProduct,
  ProductListingLayout,
  ProductCategorySection,
  PromoBanner,
} from '@/components/products/shared'

interface EuroformMultiData {
  brand: string
  logo: string
  description: string
  categories: {
    outdoor: ListingProduct[]
    indoor_wall: ListingProduct[]
    cassette_one_way: ListingProduct[]
    cassette_four_way: ListingProduct[]
    ducted: ListingProduct[]
  }
}

export default function EuroformMultiClient({ data }: { data: EuroformMultiData }) {
  const allProducts = useMemo(() => {
    const products: ListingProduct[] = []
    if (data.categories.outdoor) products.push(...data.categories.outdoor)
    if (data.categories.indoor_wall) products.push(...data.categories.indoor_wall)
    if (data.categories.cassette_one_way) products.push(...data.categories.cassette_one_way)
    if (data.categories.cassette_four_way) products.push(...data.categories.cassette_four_way)
    if (data.categories.ducted) products.push(...data.categories.ducted)
    return products
  }, [data])

  const [filteredProducts, setFilteredProducts] = useState<ListingProduct[]>(allProducts)

  const categories = [
    { key: 'outdoor', title: 'Dış Üniteler', desc: 'Tek dış üniteye birden fazla iç ünite bağlayın', products: data.categories.outdoor || [] },
    { key: 'indoor_wall', title: 'Duvar Tipi İç Üniteler', desc: 'Klasik duvar tipi iç üniteler', products: data.categories.indoor_wall || [] },
    { key: 'cassette_one_way', title: 'Tek Yöne Kaset Tipi', desc: 'Tek yöne üflemeli kaset tipi üniteler', products: data.categories.cassette_one_way || [] },
    { key: 'cassette_four_way', title: '4 Yöne Kaset Tipi', desc: '4 yöne üflemeli kaset tipi üniteler', products: data.categories.cassette_four_way || [] },
    { key: 'ducted', title: 'Kanallı Tip', desc: 'Gizli montaj kanallı tip üniteler', products: data.categories.ducted || [] },
  ]

  return (
    <ProductListingLayout
      allProducts={allProducts}
      filteredProducts={filteredProducts}
      onFilterChange={setFilteredProducts}
      brand="euroform_multi"
      accent="emerald"
      ctaDescription="Uzman ekibimiz ihtiyaçlarınızı analiz ederek en uygun multi klima çözümünü sunmaktadır."
      banner={
        <PromoBanner
          accent="emerald"
          title="Hangi Klimayı Seçeceğinize Karar Veremediniz mi?"
          description="Klimanızı seçmenizde size yardımcı olalım! İhtiyacınıza en uygun klimayı birlikte bulalım."
          href="/klimani-sec"
          buttonLabel="Klimanı Seç"
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
            brand="euroform_multi"
            accent="emerald"
          />
        )
      })}
    </ProductListingLayout>
  )
}
