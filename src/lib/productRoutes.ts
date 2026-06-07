import productsData from '@/data/products.json'

const MHI_SPLIT_SERIES = [
  'trend',
  'plus',
  'premium',
  'diamond',
  'yuksek_kapasite',
  'diamond_titanyum',
] as const

const CATEGORY_BRANDS = [
  'mhi_multi',
  'mhi_profesyonel',
  'euroform_multi',
  'euroform_profesyonel',
] as const

export type ProductRouteParam = {
  brand: string
  model: string
}

type ProductEntry = { model: string }

type BrandSplitData = Record<string, ProductEntry[] | undefined>
type BrandCategoryData = { categories?: Record<string, ProductEntry[] | undefined> }

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const products = productsData as any

/** All brand/model pairs used by /urunler/[brand]/[model] routes. */
export function getAllProductRouteParams(): ProductRouteParam[] {
  const params: ProductRouteParam[] = []

  const mhiSplit = products.mhi?.split as BrandSplitData | undefined
  if (mhiSplit) {
    for (const series of MHI_SPLIT_SERIES) {
      const items = mhiSplit[series]
      if (Array.isArray(items)) {
        for (const product of items) {
          params.push({ brand: 'mhi', model: product.model })
        }
      }
    }
  }

  const euroformSplit = products.euroform?.split as ProductEntry[] | undefined
  if (Array.isArray(euroformSplit)) {
    for (const product of euroformSplit) {
      params.push({ brand: 'euroform', model: product.model.replace('-SET', '') })
    }
  }

  for (const brandKey of CATEGORY_BRANDS) {
    const brandData = products[brandKey] as BrandCategoryData | undefined
    if (!brandData?.categories) continue

    for (const categoryKey of Object.keys(brandData.categories)) {
      const items = brandData.categories[categoryKey]
      if (!Array.isArray(items)) continue

      for (const product of items) {
        params.push({ brand: brandKey, model: product.model.replace('-SET', '') })
      }
    }
  }

  return params
}

export function getProductDetailPath({ brand, model }: ProductRouteParam): string {
  return `/urunler/${brand}/${model}`
}
