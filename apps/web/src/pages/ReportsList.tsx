import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { listSessions } from '../api/discovery';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import type { DiscoverySession } from '../types';
import { PRODUCT_CATEGORY_LABELS } from '../types';

export function ReportsList() {
  const [sessions, setSessions] = useState<DiscoverySession[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listSessions()
      .then(setSessions)
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const completedReports = useMemo(
    () => sessions
      .filter(session => session.status === 'completed')
      .sort((a, b) => {
        const left = new Date(a.completedAt ?? a.createdAt).getTime();
        const right = new Date(b.completedAt ?? b.createdAt).getTime();
        return right - left;
      }),
    [sessions],
  );

  if (loading) {
    return <LoadingSpinner message="Loading reports..." />;
  }

  return (
    <div data-testid="reports-list">
      <div style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 700 }}>Reports</h2>
        <p style={{ color: 'var(--color-gray-600)', marginTop: '0.25rem' }}>
          Browse all completed product discovery reports.
        </p>
      </div>

      {error && (
        <div className="card" style={{ background: '#fee2e2', border: '1px solid #fca5a5', marginBottom: '1.5rem' }}>
          <p style={{ color: '#991b1b', fontSize: '0.875rem' }}>
            Unable to load reports: {error}
          </p>
        </div>
      )}

      {completedReports.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '2rem' }}>
          <h3 style={{ marginBottom: '0.5rem' }}>No completed reports yet</h3>
          <p style={{ color: 'var(--color-gray-600)', marginBottom: '1rem' }}>
            Start a discovery session and your reports will appear here.
          </p>
          <Link to="/discover">
            <button className="btn-primary">Start Discovery</button>
          </Link>
        </div>
      ) : (
        <div className="card" style={{ padding: 0 }}>
          <div style={{ padding: '1rem 1.5rem', borderBottom: '1px solid var(--color-gray-200)' }}>
            <p style={{ fontSize: '0.875rem', color: 'var(--color-gray-600)' }}>
              {completedReports.length} completed report{completedReports.length === 1 ? '' : 's'}
            </p>
          </div>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--color-gray-200)' }}>
                {['Session', 'Category', 'Completed', 'Action'].map(header => (
                  <th
                    key={header}
                    style={{
                      textAlign: 'left',
                      padding: '0.75rem 1.5rem',
                      fontSize: '0.75rem',
                      fontWeight: 600,
                      color: 'var(--color-gray-600)',
                      textTransform: 'uppercase',
                    }}
                  >
                    {header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {completedReports.map((session) => {
                const categoryLabel = PRODUCT_CATEGORY_LABELS[session.productCategory] ?? session.productCategory;
                return (
                  <tr key={session.id} style={{ borderBottom: '1px solid var(--color-gray-100)' }}>
                    <td style={{ padding: '1rem 1.5rem', fontFamily: 'monospace', fontSize: '0.8rem' }}>
                      {session.id}
                    </td>
                    <td style={{ padding: '1rem 1.5rem', fontSize: '0.875rem' }}>{categoryLabel}</td>
                    <td style={{ padding: '1rem 1.5rem', color: 'var(--color-gray-600)', fontSize: '0.875rem' }}>
                      {new Date(session.completedAt ?? session.createdAt).toLocaleString('en-AU')}
                    </td>
                    <td style={{ padding: '1rem 1.5rem' }}>
                      <Link to={`/reports/${session.id}`} style={{ fontWeight: 600 }}>
                        View report
                      </Link>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}