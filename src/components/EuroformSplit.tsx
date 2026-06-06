'use client'

import { useState, useMemo } from 'react'
import {
  ListingProduct,
  ProductListingLayout,
  ProductCategorySection,
  PromoBanner,
} from '@/components/products/shared'

interface EuroformSplitData {
  brand: string
  logo: string
  description: string
  split: ListingProduct[]
}

export default function EuroformSplitClient({ data }: { data: EuroformSplitData }) {
  const allProducts = useMemo(() => data.split || [], [data])
  const [filteredProducts, setFilteredProducts] = useState<ListingProduct[]>(allProducts)

  return (
    <ProductListingLayout
      allProducts={allProducts}
      filteredProducts={filteredProducts}
      onFilterChange={setFilteredProducts}
      brand="euroform"
      accent="orange"
      banner={
        <PromoBanner
          accent="orange"
          title="Hangi Klimayı Seçeceğinize Karar Veremediniz mi?"
          description="Klimanızı seçmenizde size yardımcı olalım! İhtiyacınıza en uygun klimayı birlikte bulalım."
          href="/klimani-sec"
          buttonLabel="Klimanı Seç"
        />
      }
    >
      <ProductCategorySection
        title="Wing Serisi"
        desc="Enerji verimli ve ekonomik split klima çözümleri"
        products={filteredProducts}
        brand="euroform"
        accent="orange"
      />
    </ProductListingLayout>
  )
}
