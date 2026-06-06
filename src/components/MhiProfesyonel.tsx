'use client'

import { useState, useMemo } from 'react'
import {
  ListingProduct,
  ProductListingLayout,
  ProductCategorySection,
  PromoBanner,
} from '@/components/products/shared'

interface MhiProfesyonelData {
  brand: string
  logo: string
  description: string
  categories: {
    cassette: ListingProduct[]
    salon: ListingProduct[]
    ducted_medium: ListingProduct[]
    ducted_high: ListingProduct[]
    ceiling: ListingProduct[]
  }
}

export default function MhiProfesyonelClient({ data }: { data: MhiProfesyonelData }) {
  const allProducts = useMemo(() => {
    const products: ListingProduct[] = []
    if (data.categories.cassette) products.push(...data.categories.cassette)
    if (data.categories.salon) products.push(...data.categories.salon)
    if (data.categories.ducted_medium) products.push(...data.categories.ducted_medium)
    if (data.categories.ducted_high) products.push(...data.categories.ducted_high)
    if (data.categories.ceiling) products.push(...data.categories.ceiling)
    return products
  }, [data])

  const [filteredProducts, setFilteredProducts] = useState<ListingProduct[]>(allProducts)

  const categories = [
    { key: 'cassette', title: 'Kaset Tipi', desc: 'Tavan arasına gizlenen kaset tipi üniteler', products: data.categories.cassette || [] },
    { key: 'salon', title: 'Salon Tipi', desc: 'Geniş alanlar için salon tipi üniteler', products: data.categories.salon || [] },
    { key: 'ducted_medium', title: 'Orta Statik Basınç', desc: 'Orta basınçlı kanal tipi sistemler', products: data.categories.ducted_medium || [] },
    { key: 'ducted_high', title: 'Yüksek Statik Basınç', desc: 'Yüksek basınçlı kanal tipi sistemler', products: data.categories.ducted_high || [] },
    { key: 'ceiling', title: 'Tavan Tipi', desc: 'Tavana monte tavan tipi üniteler', products: data.categories.ceiling || [] },
  ]

  return (
    <ProductListingLayout
      allProducts={allProducts}
      filteredProducts={filteredProducts}
      onFilterChange={setFilteredProducts}
      brand="mhi_profesyonel"
      accent="red"
      ctaDescription="Uzman ekibimiz ihtiyaçlarınızı analiz ederek en uygun profesyonel klima çözümünü sunmaktadır."
      banner={
        <PromoBanner
          accent="purple"
          title="Profesyonel Klimanızı Seçmekte Zorlanıyor musunuz?"
          description="İşletmenize en uygun klimayı seçmenizde size yardımcı olalım!"
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
            brand="mhi_profesyonel"
            accent="red"
          />
        )
      })}
    </ProductListingLayout>
  )
}
