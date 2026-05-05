import { describe, it, expect } from 'vitest';
import { PRODUCT_CATEGORY_LABELS } from '../types';

describe('PRODUCT_CATEGORY_LABELS', () => {
  it('has label for TRANS_AND_SAVINGS_ACCOUNTS', () => {
    expect(PRODUCT_CATEGORY_LABELS['TRANS_AND_SAVINGS_ACCOUNTS']).toBe('Transaction & Savings');
  });

  it('has label for RESIDENTIAL_MORTGAGES', () => {
    expect(PRODUCT_CATEGORY_LABELS['RESIDENTIAL_MORTGAGES']).toBe('Home Loans');
  });

  it('has 12 categories', () => {
    expect(Object.keys(PRODUCT_CATEGORY_LABELS).length).toBe(12);
  });
});
