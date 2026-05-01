import React, { useState, useEffect } from 'react';
import { listProviders } from '../api/providers';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import type { Provider } from '../types';

export function SyncStatus() {
  const [providers, setProviders] = useState<Provider[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastRefresh, setLastRefresh] = useState(new Date());

  useEffect(() => {
    const fetchData = () => {
      listProviders()
        .then(setProviders)
        .catch(console.error)
        .finally(() => { setLoading(false); setLastRefresh(new Date()); });
    };
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <LoadingSpinner message="Loading sync status..." />;

  return (
    <div data-testid="sync-status">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 700 }}>Provider Sync Status</h2>
          <p style={{ color: 'var(--color-gray-600)', fontSize: '0.875rem', marginTop: '0.25rem' }}>
            Last refreshed: {lastRefresh.toLocaleTimeString()} (auto-refreshes every 30s)
          </p>
        </div>
      </div>
      <div className="card">
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--color-gray-200)' }}>
              {['Provider', 'Status', 'Last Sync', 'Mode'].map(h => (
                <th key={h} style={{ textAlign: 'left', padding: '0.75rem 1rem', fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-gray-600)', textTransform: 'uppercase' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {providers.length === 0 ? (
              [
                { name: 'Harbour Bank', status: 'active' },
                { name: 'Southern Cross Bank', status: 'active' },
                { name: 'Pacific Coast Bank', status: 'active' },
              ].map((p, i) => (
                <tr key={i} style={{ borderBottom: '1px solid var(--color-gray-100)' }}>
                  <td style={{ padding: '1rem' }}>🏦 {p.name}</td>
                  <td style={{ padding: '1rem' }}><span className="badge badge-success">✓ Active</span></td>
                  <td style={{ padding: '1rem', color: 'var(--color-gray-600)', fontSize: '0.875rem' }}>Demo mode</td>
                  <td style={{ padding: '1rem' }}><span className="badge badge-info">CDR Public</span></td>
                </tr>
              ))
            ) : providers.map(provider => (
              <tr key={provider.id} style={{ borderBottom: '1px solid var(--color-gray-100)' }}>
                <td style={{ padding: '1rem' }}>🏦 {provider.brandName || provider.name}</td>
                <td style={{ padding: '1rem' }}>
                  <span className={`badge ${provider.isActive ? 'badge-success' : 'badge-error'}`}>
                    {provider.isActive ? '✓ Active' : '✗ Inactive'}
                  </span>
                </td>
                <td style={{ padding: '1rem', color: 'var(--color-gray-600)', fontSize: '0.875rem' }}>
                  {provider.lastSyncAt ? new Date(provider.lastSyncAt).toLocaleString() : 'Never'}
                </td>
                <td style={{ padding: '1rem' }}><span className="badge badge-info">CDR Public</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
