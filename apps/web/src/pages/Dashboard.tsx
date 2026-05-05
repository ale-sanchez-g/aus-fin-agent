import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { listSessions } from '../api/discovery';
import { listProviders } from '../api/providers';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import type { DiscoverySession, Provider } from '../types';

export function Dashboard() {
  const [sessions, setSessions] = useState<DiscoverySession[]>([]);
  const [providers, setProviders] = useState<Provider[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([listSessions(), listProviders()])
      .then(([s, p]) => { setSessions(s); setProviders(p); })
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner message="Loading dashboard..." />;

  return (
    <div data-testid="dashboard">
      <div style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--color-gray-900)' }}>
          Dashboard
        </h2>
        <p style={{ color: 'var(--color-gray-600)', marginTop: '0.25rem' }}>
          Australian open banking product discovery platform
        </p>
      </div>

      {/* CDR Notice */}
      <div className="card" style={{
        background: '#eff6ff',
        border: '1px solid #bfdbfe',
        marginBottom: '1.5rem',
        display: 'flex',
        gap: '0.75rem',
        alignItems: 'flex-start',
      }}>
        <span style={{ fontSize: '1.25rem' }}>ℹ️</span>
        <div>
          <strong style={{ color: 'var(--color-primary)', fontSize: '0.875rem' }}>
            CDR Public Data Mode Active
          </strong>
          <p style={{ fontSize: '0.8rem', color: '#1e40af', marginTop: '0.25rem' }}>
            This platform operates with publicly available product reference data from the Consumer Data Right (CDR) ecosystem.
            Consented consumer data access requires CDR accreditation and is disabled by default.
          </p>
        </div>
      </div>

      {error && (
        <div className="card" style={{ background: '#fee2e2', border: '1px solid #fca5a5', marginBottom: '1.5rem' }}>
          <p style={{ color: '#991b1b', fontSize: '0.875rem' }}>⚠️ API connection error: {error}. Showing demo data.</p>
        </div>
      )}

      {/* Stats cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
        {[
          { label: 'Active Providers', value: providers.length || 3, icon: '🏦', color: 'var(--color-primary)' },
          { label: 'Discovery Sessions', value: sessions.length, icon: '🔍', color: 'var(--color-success)' },
          { label: 'Completed Reports', value: sessions.filter(s => s.status === 'completed').length, icon: '📄', color: 'var(--color-accent)' },
        ].map(stat => (
          <div key={stat.label} className="card" style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div style={{
              width: 48,
              height: 48,
              borderRadius: '12px',
              background: `${stat.color}15`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1.5rem',
            }}>
              {stat.icon}
            </div>
            <div>
              <p style={{ fontSize: '1.75rem', fontWeight: 700, color: stat.color }}>{stat.value}</p>
              <p style={{ fontSize: '0.8rem', color: 'var(--color-gray-600)' }}>{stat.label}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Quick start */}
      <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
        <h3 style={{ fontSize: '1.25rem', marginBottom: '0.5rem' }}>Start a Product Discovery</h3>
        <p style={{ color: 'var(--color-gray-600)', marginBottom: '1.5rem' }}>
          Use our AI-assisted wizard to find the best Australian financial products for your needs.
        </p>
        <Link to="/discover">
          <button className="btn-primary" style={{ padding: '0.75rem 2rem', fontSize: '1rem' }}>
            🔍 Start Discovery
          </button>
        </Link>
      </div>
    </div>
  );
}
