import { describe, it, expect } from 'vitest';

function formatCurrency(amount: number, currency = 'AUD'): string {
  return new Intl.NumberFormat('en-AU', { style: 'currency', currency }).format(amount);
}

function formatRate(rate: string | number): string {
  const n = typeof rate === 'string' ? parseFloat(rate) : rate;
  return `${(n * 100).toFixed(2)}% p.a.`;
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-AU');
}

describe('formatCurrency', () => {
  it('formats AUD amounts', () => {
    expect(formatCurrency(5)).toBe('$5.00');
    expect(formatCurrency(0)).toBe('$0.00');
    expect(formatCurrency(1234.56)).toBe('$1,234.56');
  });
});

describe('formatRate', () => {
  it('converts decimal rate to percentage string', () => {
    expect(formatRate('0.0475')).toBe('4.75% p.a.');
    expect(formatRate('0.0624')).toBe('6.24% p.a.');
    expect(formatRate(0.05)).toBe('5.00% p.a.');
  });
});

describe('formatDate', () => {
  it('formats ISO date string', () => {
    const result = formatDate('2025-01-15T00:00:00Z');
    expect(result).toContain('2025');
  });
});
