import React, { useState, useEffect } from 'react';
import { listProducts } from '../api/products';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { EmptyState } from '../components/ui/EmptyState';
import type { Product } from '../types';
import { PRODUCT_CATEGORY_LABELS } from '../types';

const DEMO_PRODUCTS: Product[] = [
  {
    id: '1', productId: 'prod-1', productCategory: 'TRANS_AND_SAVINGS_ACCOUNTS',
    name: 'Everyday Saver', description: 'High-interest savings account with no monthly fees',
    brand: 'harbour-bank', brandName: 'Harbour Bank', isTailored: false,
    features: [{ featureType: 'NPP_PAYID' }, { featureType: 'DIGITAL_BANKING' }],
    fees: [], depositRates: [{ rateType: 'VARIABLE', rate: '0.0450' }],
    lendingRates: [], eligibility: [],
  },
  {
    id: '2', productId: 'prod-2', productCategory: 'TRANS_AND_SAVINGS_ACCOUNTS',
    name: 'Premium Saver Plus', description: 'Bonus interest when you grow your balance',
    brand: 'southern-cross', brandName: 'Southern Cross Bank', isTailored: false,
    features: [{ featureType: 'DIGITAL_BANKING' }, { featureType: 'FREE_TXNS' }],
    fees: [{ name: 'Monthly Fee', feeType: 'PERIODIC', amount: '5.00' }],
    depositRates: [{ rateType: 'VARIABLE', rate: '0.0520' }],
    lendingRates: [], eligibility: [],
  },
  {
    id: '3', productId: 'prod-3', productCategory: 'TRANS_AND_SAVINGS_ACCOUNTS',
    name: 'Youth Account', description: 'For customers aged 18-30',
    brand: 'pacific-coast', brandName: 'Pacific Coast Bank', isTailored: false,
    features: [{ featureType: 'DIGITAL_BANKING' }, { featureType: 'NPP_PAYID' }, { featureType: 'FREE_TXNS' }],
    fees: [],
    depositRates: [{ rateType: 'VARIABLE', rate: '0.0480' }],
    lendingRates: [], eligibility: [{ eligibilityType: 'MAX_AGE', additionalValue: '30' }],
  },
];

export function ProductComparison() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listProducts({ pageSize: 10 })
      .then(res => setProducts(res.items.length > 0 ? res.items : DEMO_PRODUCTS))
      .catch(() => setProducts(DEMO_PRODUCTS))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner message="Loading products..." />;

  return (
    <div data-testid="product-comparison">
      <div style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 700 }}>Product Comparison</h2>
        <p style={{ color: 'var(--color-gray-600)', fontSize: '0.875rem', marginTop: '0.25rem' }}>
          Compare financial products side by side
        </p>
      </div>

      <div className="card" style={{ background: '#fef3c7', border: '1px solid #fcd34d', marginBottom: '1.5rem' }}>
        <p style={{ fontSize: '0.8rem', color: '#92400e' }}>
          ⚠️ <strong>Not Financial Advice:</strong> Product information is sourced from public CDR data and is for comparison purposes only.
          This does not constitute personal financial advice. Consult a licensed financial adviser before making financial decisions.
        </p>
      </div>

      {products.length === 0 ? (
        <EmptyState title="No products found" description="Try adjusting your filters or sync provider data." />
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', background: 'white', borderRadius: 'var(--radius)', boxShadow: 'var(--shadow)' }}>
            <thead>
              <tr style={{ background: 'var(--color-gray-50)', borderBottom: '2px solid var(--color-gray-200)' }}>
                <th style={{ padding: '1rem', textAlign: 'left', fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-gray-600)', textTransform: 'uppercase', width: '160px' }}>
                  Feature
                </th>
                {products.map(p => (
                  <th key={p.id} style={{ padding: '1rem', textAlign: 'left', fontSize: '0.875rem', fontWeight: 600 }}>
                    <div>{p.name}</div>
                    <div style={{ fontWeight: 400, fontSize: '0.8rem', color: 'var(--color-gray-600)' }}>{p.brandName}</div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              <tr style={{ borderBottom: '1px solid var(--color-gray-100)' }}>
                <td style={{ padding: '1rem', fontWeight: 500, fontSize: '0.875rem', color: 'var(--color-gray-600)', background: 'var(--color-gray-50)' }}>Category</td>
                {products.map(p => (
                  <td key={p.id} style={{ padding: '1rem', fontSize: '0.875rem' }}>
                    {PRODUCT_CATEGORY_LABELS[p.productCategory]}
                  </td>
                ))}
              </tr>
              <tr style={{ borderBottom: '1px solid var(--color-gray-100)' }}>
                <td style={{ padding: '1rem', fontWeight: 500, fontSize: '0.875rem', color: 'var(--color-gray-600)', background: 'var(--color-gray-50)' }}>Deposit Rates</td>
                {products.map(p => (
                  <td key={p.id} style={{ padding: '1rem', fontSize: '0.875rem' }}>
                    {p.depositRates.length > 0
                      ? p.depositRates.map((r, i) => (
                          <div key={i}>
                            <strong style={{ color: 'var(--color-success)' }}>
                              {(parseFloat(r.rate) * 100).toFixed(2)}% p.a.
                            </strong>
                            <span style={{ fontSize: '0.75rem', color: 'var(--color-gray-400)', marginLeft: '0.25rem' }}>{r.rateType}</span>
                          </div>
                        ))
                      : <span style={{ color: 'var(--color-gray-400)' }}>—</span>
                    }
                  </td>
                ))}
              </tr>
              <tr style={{ borderBottom: '1px solid var(--color-gray-100)' }}>
                <td style={{ padding: '1rem', fontWeight: 500, fontSize: '0.875rem', color: 'var(--color-gray-600)', background: 'var(--color-gray-50)' }}>Monthly Fees</td>
                {products.map(p => (
                  <td key={p.id} style={{ padding: '1rem', fontSize: '0.875rem' }}>
                    {p.fees.length === 0
                      ? <span style={{ color: 'var(--color-success)', fontWeight: 600 }}>No fees</span>
                      : p.fees.map((f, i) => (
                          <div key={i}>${f.amount || '0'} {f.name}</div>
                        ))
                    }
                  </td>
                ))}
              </tr>
              <tr style={{ borderBottom: '1px solid var(--color-gray-100)' }}>
                <td style={{ padding: '1rem', fontWeight: 500, fontSize: '0.875rem', color: 'var(--color-gray-600)', background: 'var(--color-gray-50)' }}>Features</td>
                {products.map(p => (
                  <td key={p.id} style={{ padding: '1rem', fontSize: '0.8rem' }}>
                    {p.features.length === 0
                      ? <span style={{ color: 'var(--color-gray-400)' }}>—</span>
                      : (
                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem' }}>
                            {p.features.map((f, i) => (
                              <span key={i} className="badge badge-neutral">{f.featureType.replace(/_/g, ' ')}</span>
                            ))}
                          </div>
                        )
                    }
                  </td>
                ))}
              </tr>
              <tr>
                <td style={{ padding: '1rem', fontWeight: 500, fontSize: '0.875rem', color: 'var(--color-gray-600)', background: 'var(--color-gray-50)' }}>Eligibility</td>
                {products.map(p => (
                  <td key={p.id} style={{ padding: '1rem', fontSize: '0.875rem' }}>
                    {p.eligibility.length === 0
                      ? <span style={{ color: 'var(--color-success)' }}>Open to all</span>
                      : p.eligibility.map((e, i) => (
                          <div key={i} style={{ fontSize: '0.8rem', color: 'var(--color-gray-600)' }}>
                            {e.eligibilityType}: {e.additionalValue || e.additionalInfo || ''}
                          </div>
                        ))
                    }
                  </td>
                ))}
              </tr>
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
