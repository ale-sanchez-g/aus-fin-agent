import React, { useState } from 'react';
import { searchProductsByIntent } from '../api/products';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { EmptyState } from '../components/ui/EmptyState';
import type { Product } from '../types';
import { PRODUCT_CATEGORY_LABELS } from '../types';

const INTENT_SUGGESTIONS = [
  'Best savings accounts with no monthly fees',
  'High interest term deposits',
  'Home loans with low rates',
  'Credit cards with rewards',
  'Personal loans for car purchase',
  'Everyday transaction accounts',
];

export function ProductComparison() {
  const [intent, setIntent] = useState('');
  const [products, setProducts] = useState<Product[]>([]);
  const [inferredCategory, setInferredCategory] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);

  async function handleDiscover(customIntent?: string) {
    const query = (customIntent ?? intent).trim();
    if (!query) return;

    setIntent(query);
    setLoading(true);
    setError(null);
    setHasSearched(true);

    try {
      const result = await searchProductsByIntent(query, 6);
      setProducts(result.products);
      setInferredCategory(result.inferredCategory);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Discovery failed';
      setError(message);
      setProducts([]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div data-testid="product-comparison">
      <div style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 700 }}>Product Comparison</h2>
        <p style={{ color: 'var(--color-gray-600)', fontSize: '0.875rem', marginTop: '0.25rem' }}>
          Describe what you are looking for and our AI agent will find matching CDR products.
        </p>
      </div>

      <div className="card" style={{ background: '#fef3c7', border: '1px solid #fcd34d', marginBottom: '1.5rem' }}>
        <p style={{ fontSize: '0.8rem', color: '#92400e' }}>
          ⚠️ <strong>Not Financial Advice:</strong> Product information is sourced from public CDR data and is for comparison purposes only.
          This does not constitute personal financial advice. Consult a licensed financial adviser before making financial decisions.
        </p>
      </div>

      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <label htmlFor="intent-input" style={{ display: 'block', fontWeight: 600, marginBottom: '0.5rem', fontSize: '0.875rem' }}>
          What are you looking for?
        </label>
        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'stretch' }}>
          <input
            id="intent-input"
            type="text"
            value={intent}
            onChange={e => setIntent(e.target.value)}
            onKeyDown={e => {
              if (e.key === 'Enter') {
                void handleDiscover();
              }
            }}
            placeholder="e.g. best savings account with no fees"
            style={{
              flex: 1,
              padding: '0.625rem 0.875rem',
              border: '1px solid var(--color-gray-300)',
              borderRadius: 'var(--radius)',
              fontSize: '0.875rem',
              outline: 'none',
            }}
          />
          <button
            onClick={() => {
              void handleDiscover();
            }}
            disabled={loading || !intent.trim()}
            style={{
              padding: '0.625rem 1.25rem',
              background: loading || !intent.trim() ? 'var(--color-gray-300)' : 'var(--color-primary)',
              color: 'white',
              border: 'none',
              borderRadius: 'var(--radius)',
              fontWeight: 600,
              fontSize: '0.875rem',
              cursor: loading || !intent.trim() ? 'not-allowed' : 'pointer',
              whiteSpace: 'nowrap',
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
            }}
          >
            {loading ? 'Discovering...' : 'Discover Products'}
          </button>
        </div>

        <div style={{ marginTop: '0.75rem', display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
          {INTENT_SUGGESTIONS.map(suggestion => (
            <button
              key={suggestion}
              onClick={() => {
                void handleDiscover(suggestion);
              }}
              disabled={loading}
              style={{
                padding: '0.25rem 0.625rem',
                background: 'var(--color-gray-100)',
                border: '1px solid var(--color-gray-300)',
                borderRadius: '999px',
                fontSize: '0.75rem',
                cursor: loading ? 'not-allowed' : 'pointer',
                color: 'var(--color-gray-700)',
              }}
            >
              {suggestion}
            </button>
          ))}
        </div>

        {inferredCategory && !loading && (
          <p style={{ marginTop: '0.75rem', fontSize: '0.8rem', color: 'var(--color-gray-500)' }}>
            Detected category:{' '}
            <span style={{ fontWeight: 600, color: 'var(--color-primary)' }}>
              {PRODUCT_CATEGORY_LABELS[inferredCategory as keyof typeof PRODUCT_CATEGORY_LABELS] ?? inferredCategory}
            </span>
          </p>
        )}
      </div>

      {loading && <LoadingSpinner message="AI agent is querying the Open Banking MCP..." />}

      {error && (
        <div className="card" style={{ background: '#fee2e2', border: '1px solid #fca5a5', color: '#991b1b', fontSize: '0.875rem' }}>
          {error}
        </div>
      )}

      {!loading && !error && hasSearched && products.length === 0 && (
        <EmptyState title="No products found" description="Try a different query or check that the Open Banking service is reachable." />
      )}

      {!loading && !error && !hasSearched && (
        <div style={{ textAlign: 'center', padding: '3rem 1rem', color: 'var(--color-gray-400)' }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem' }}>Search by intent to populate products.</div>
        </div>
      )}

      {!loading && products.length > 0 && (
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
                    <div style={{ fontWeight: 400, fontSize: '0.8rem', color: 'var(--color-gray-600)' }}>{p.brandName || p.brand}</div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              <tr style={{ borderBottom: '1px solid var(--color-gray-100)' }}>
                <td style={{ padding: '1rem', fontWeight: 500, fontSize: '0.875rem', color: 'var(--color-gray-600)', background: 'var(--color-gray-50)' }}>Category</td>
                {products.map(p => (
                  <td key={p.id} style={{ padding: '1rem', fontSize: '0.875rem' }}>
                    {PRODUCT_CATEGORY_LABELS[p.productCategory] ?? p.productCategory}
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
                      : <span style={{ color: 'var(--color-gray-400)' }}>-</span>}
                  </td>
                ))}
              </tr>
              <tr style={{ borderBottom: '1px solid var(--color-gray-100)' }}>
                <td style={{ padding: '1rem', fontWeight: 500, fontSize: '0.875rem', color: 'var(--color-gray-600)', background: 'var(--color-gray-50)' }}>Lending Rates</td>
                {products.map(p => (
                  <td key={p.id} style={{ padding: '1rem', fontSize: '0.875rem' }}>
                    {p.lendingRates.length > 0
                      ? p.lendingRates.map((r, i) => (
                          <div key={i}>
                            <strong style={{ color: '#d97706' }}>
                              {(parseFloat(r.rate) * 100).toFixed(2)}% p.a.
                            </strong>
                            {r.comparisonRate && (
                              <span style={{ fontSize: '0.75rem', color: 'var(--color-gray-400)', marginLeft: '0.25rem' }}>
                                comp. {(parseFloat(r.comparisonRate) * 100).toFixed(2)}%
                              </span>
                            )}
                          </div>
                        ))
                      : <span style={{ color: 'var(--color-gray-400)' }}>-</span>}
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
                        ))}
                  </td>
                ))}
              </tr>
              <tr style={{ borderBottom: '1px solid var(--color-gray-100)' }}>
                <td style={{ padding: '1rem', fontWeight: 500, fontSize: '0.875rem', color: 'var(--color-gray-600)', background: 'var(--color-gray-50)' }}>Features</td>
                {products.map(p => (
                  <td key={p.id} style={{ padding: '1rem', fontSize: '0.8rem' }}>
                    {p.features.length === 0
                      ? <span style={{ color: 'var(--color-gray-400)' }}>-</span>
                      : (
                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem' }}>
                            {p.features.map((f, i) => (
                              <span key={i} className="badge badge-neutral">{f.featureType.replace(/_/g, ' ')}</span>
                            ))}
                          </div>
                        )}
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
                        ))}
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
