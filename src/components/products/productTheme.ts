import type { CSSProperties } from 'react'

export type ProductAccent = 'red' | 'orange' | 'blue' | 'purple' | 'teal' | 'emerald'

export const BRAND_ACCENT: Record<string, ProductAccent> = {
  mhi: 'red',
  euroform: 'orange',
  mhi_multi: 'blue',
  mhi_profesyonel: 'purple',
  euroform_multi: 'emerald',
  euroform_profesyonel: 'teal',
}

export const DETAIL_HERO: Record<ProductAccent, {
  gradientClass: string
  subtitleClass: string
  btuBadge: string
  catalogBtn: string
  quoteBtn: string
}> = {
  red: {
    gradientClass: 'bg-gradient-to-r from-red-700 to-red-600',
    subtitleClass: 'text-red-100',
    btuBadge: 'bg-red-500',
    catalogBtn: 'text-red-600 active:bg-gray-50 md:hover:bg-gray-50',
    quoteBtn: 'bg-red-500 active:bg-red-700 md:hover:bg-red-700',
  },
  orange: {
    gradientClass: 'bg-gradient-to-r from-orange-700 to-orange-600',
    subtitleClass: 'text-orange-100',
    btuBadge: 'bg-orange-500',
    catalogBtn: 'text-orange-600 active:bg-gray-50 md:hover:bg-gray-50',
    quoteBtn: 'bg-orange-500 active:bg-orange-700 md:hover:bg-orange-700',
  },
  blue: {
    gradientClass: 'bg-gradient-to-r from-blue-700 to-blue-600',
    subtitleClass: 'text-blue-100',
    btuBadge: 'bg-blue-500',
    catalogBtn: 'text-blue-600 active:bg-gray-50 md:hover:bg-gray-50',
    quoteBtn: 'bg-blue-500 active:bg-blue-700 md:hover:bg-blue-700',
  },
  purple: {
    gradientClass: 'bg-gradient-to-r from-purple-700 to-purple-600',
    subtitleClass: 'text-purple-100',
    btuBadge: 'bg-purple-500',
    catalogBtn: 'text-purple-600 active:bg-gray-50 md:hover:bg-gray-50',
    quoteBtn: 'bg-purple-500 active:bg-purple-700 md:hover:bg-purple-700',
  },
  teal: {
    gradientClass: 'bg-gradient-to-r from-teal-700 to-teal-600',
    subtitleClass: 'text-teal-100',
    btuBadge: 'bg-teal-500',
    catalogBtn: 'text-teal-600 active:bg-gray-50 md:hover:bg-gray-50',
    quoteBtn: 'bg-teal-500 active:bg-teal-700 md:hover:bg-teal-700',
  },
  emerald: {
    gradientClass: 'bg-gradient-to-r from-emerald-700 to-emerald-600',
    subtitleClass: 'text-emerald-100',
    btuBadge: 'bg-emerald-500',
    catalogBtn: 'text-emerald-600 active:bg-gray-50 md:hover:bg-gray-50',
    quoteBtn: 'bg-emerald-500 active:bg-emerald-700 md:hover:bg-emerald-700',
  },
}

export const ACCENT_THEME: Record<ProductAccent, {
  badge: string
  price: string
  inspect: string
  ctaBtn: string
  banner: string
  bannerSub: string
  bannerBtn: string
}> = {
  red: {
    badge: 'bg-red-100 text-red-700',
    price: 'text-red-600',
    inspect: 'text-red-600',
    ctaBtn: 'bg-red-600 active:bg-red-700 md:hover:bg-red-700',
    banner: 'bg-gradient-to-r from-red-600 to-red-700',
    bannerSub: 'text-red-100',
    bannerBtn: 'text-red-700 active:bg-red-50 md:hover:bg-red-50',
  },
  orange: {
    badge: 'bg-orange-100 text-orange-700',
    price: 'text-orange-600',
    inspect: 'text-orange-600',
    ctaBtn: 'bg-orange-600 active:bg-orange-700 md:hover:bg-orange-700',
    banner: 'bg-gradient-to-r from-orange-500 to-orange-600',
    bannerSub: 'text-orange-100',
    bannerBtn: 'text-orange-600 active:bg-orange-50 md:hover:bg-orange-50',
  },
  blue: {
    badge: 'bg-red-100 text-red-700',
    price: 'text-red-600',
    inspect: 'text-red-600',
    ctaBtn: 'bg-red-600 active:bg-red-700 md:hover:bg-red-700',
    banner: 'bg-gradient-to-r from-blue-600 to-blue-700',
    bannerSub: 'text-blue-100',
    bannerBtn: 'text-blue-700 active:bg-blue-50 md:hover:bg-blue-50',
  },
  purple: {
    badge: 'bg-red-100 text-red-700',
    price: 'text-red-600',
    inspect: 'text-red-600',
    ctaBtn: 'bg-red-600 active:bg-red-700 md:hover:bg-red-700',
    banner: 'bg-gradient-to-r from-purple-600 to-purple-700',
    bannerSub: 'text-purple-100',
    bannerBtn: 'text-purple-700 active:bg-purple-50 md:hover:bg-purple-50',
  },
  teal: {
    badge: 'bg-teal-100 text-teal-700',
    price: 'text-teal-600',
    inspect: 'text-teal-600',
    ctaBtn: 'bg-teal-600 active:bg-teal-700 md:hover:bg-teal-700',
    banner: 'bg-gradient-to-r from-teal-600 to-teal-700',
    bannerSub: 'text-teal-100',
    bannerBtn: 'text-teal-700 active:bg-teal-50 md:hover:bg-teal-50',
  },
  emerald: {
    badge: 'bg-emerald-100 text-emerald-700',
    price: 'text-emerald-600',
    inspect: 'text-emerald-600',
    ctaBtn: 'bg-emerald-600 active:bg-emerald-700 md:hover:bg-emerald-700',
    banner: 'bg-gradient-to-r from-emerald-600 to-emerald-700',
    bannerSub: 'text-emerald-100',
    bannerBtn: 'text-emerald-700 active:bg-emerald-50 md:hover:bg-emerald-50',
  },
}

export function getProductAccent(brand: string): ProductAccent {
  return BRAND_ACCENT[brand] ?? 'red'
}

export function formatBtu(btu: number): string {
  return `${btu.toLocaleString('tr-TR')} BTU`
}

/** Ürün detay teknik özellikler tablosu — marka rengine göre zebra tonları */
export const SPEC_TABLE_THEME: Record<ProductAccent, {
  headerBg: string
  border: string
  rowOdd: string
  rowEven: string
  labelOdd: string
  labelEven: string
  text: string
}> = {
  red: {
    headerBg: '#b91c1c',
    border: '#fecaca',
    rowOdd: '#ffffff',
    rowEven: '#fef2f2',
    labelOdd: '#fee2e2',
    labelEven: '#fca5a5',
    text: '#1f2937',
  },
  orange: {
    headerBg: '#c2410c',
    border: '#fed7aa',
    rowOdd: '#ffffff',
    rowEven: '#fff7ed',
    labelOdd: '#ffedd5',
    labelEven: '#fdba74',
    text: '#1f2937',
  },
  blue: {
    headerBg: '#1d4ed8',
    border: '#bfdbfe',
    rowOdd: '#ffffff',
    rowEven: '#eff6ff',
    labelOdd: '#dbeafe',
    labelEven: '#93c5fd',
    text: '#1f2937',
  },
  purple: {
    headerBg: '#7e22ce',
    border: '#e9d5ff',
    rowOdd: '#ffffff',
    rowEven: '#faf5ff',
    labelOdd: '#f3e8ff',
    labelEven: '#d8b4fe',
    text: '#1f2937',
  },
  teal: {
    headerBg: '#0f766e',
    border: '#99f6e4',
    rowOdd: '#ffffff',
    rowEven: '#f0fdfa',
    labelOdd: '#ccfbf1',
    labelEven: '#5eead4',
    text: '#1f2937',
  },
  emerald: {
    headerBg: '#047857',
    border: '#a7f3d0',
    rowOdd: '#ffffff',
    rowEven: '#ecfdf5',
    labelOdd: '#d1fae5',
    labelEven: '#6ee7b7',
    text: '#1f2937',
  },
}

export function getSpecTableStyle(accent: ProductAccent): CSSProperties {
  const t = SPEC_TABLE_THEME[accent]
  return {
    '--spec-header-bg': t.headerBg,
    '--spec-border': t.border,
    '--spec-row-odd': t.rowOdd,
    '--spec-row-even': t.rowEven,
    '--spec-label-odd': t.labelOdd,
    '--spec-label-even': t.labelEven,
    '--spec-text': t.text,
  } as CSSProperties
}
