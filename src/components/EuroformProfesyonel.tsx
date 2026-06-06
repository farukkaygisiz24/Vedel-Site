'use client'

import { useState, useMemo } from 'react'
import {
  ListingProduct,
  ProductListingLayout,
  ProductCategorySection,
  PromoBanner,
} from '@/components/products/shared'

interface EuroformProfesyonelData {
  brand: string
  logo: string
  description: string
  categories: {
    cassette: ListingProduct[]
    salon: ListingProduct[]
    ducted: ListingProduct[]
  }
}

export default function EuroformProfesyonelClient({ data }: { data: EuroformProfesyonelData }) {
  const allProducts = useMemo(() => {
    const products: ListingProduct[] = []
    if (data.categories.cassette) products.push(...data.categories.cassette)
    if (data.categories.salon) products.push(...data.categories.salon)
    if (data.categories.ducted) products.push(...data.categories.ducted)
    return products
  }, [data])

  const [filteredProducts, setFilteredProducts] = useState<ListingProduct[]>(allProducts)

  const categories = [
    { key: 'cassette', title: 'Kaset Tipi', desc: 'Tavan arasına gizlenen kaset tipi üniteler', products: data.categories.cassette || [] },
    { key: 'salon', title: 'Salon Tipi', desc: 'Geniş alanlar için salon tipi üniteler', products: data.categories.salon || [] },
    { key: 'ducted', title: 'Kanallı Tip', desc: 'Gizli montaj kanallı tip sistemler', products: data.categories.ducted || [] },
  ]

  return (
    <ProductListingLayout
      allProducts={allProducts}
      filteredProducts={filteredProducts}
      onFilterChange={setFilteredProducts}
      brand="euroform_profesyonel"
      accent="teal"
      ctaDescription="Uzman ekibimiz ihtiyaçlarınızı analiz ederek en uygun profesyonel klima çözümünü sunmaktadır."
      banner={
        <PromoBanner
          accent="teal"
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
            brand="euroform_profesyonel"
            accent="teal"
          />
        )
      })}
    </ProductListingLayout>
  )
}
