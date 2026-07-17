// src/utils/styleUtils.js
// Örnek 6.1: Dinamik Sınıf Birleştirme Yardımcısı
// Tailwind sınıflarını güvenle birleştirmek ve çakışmaları önlemek için.
// shadcn/ui standardı: clsx + tailwind-merge kombinasyonu

import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Tailwind class'larını güvenli şekilde birleştirir.
 * @param {...any} inputs - clsx kabul eden değerler
 * @returns {string}
 */
export const cn = (...inputs) => {
  return twMerge(clsx(inputs));
};
