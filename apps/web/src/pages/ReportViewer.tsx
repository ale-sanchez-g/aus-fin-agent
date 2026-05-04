import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getReport } from '../api/reports';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import type { DiscoveryReport, RecommendationResult } from '../types';

export function ReportViewer() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const [report, setReport] = useState<DiscoveryReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId) return;
    getReport(sessionId)
      .then(setReport)
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, [sessionId]);

  if (loading) return <LoadingSpinner message="Loading report..." />;

  if (error || !report) {
    return (
      <div data-testid="report-viewer">
        <div style={{ marginBottom: '1.5rem' }}>
          <Link to="/reports" style={{ fontSize: '0.875rem', color: 'var(--color-gray-600)' }}>← Back to Reports</Link>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginTop: '0.5rem' }}>Discovery Report</h2>
        </div>
        <div className="card" style={{ background: '#fee2e2', border: '1px solid #fca5a5' }}>
          <p style={{ color: '#991b1b' }}>
            {error || 'Report not found. The session may still be processing.'}
          </p>
          <Link to="/discover" style={{ display: 'inline-block', marginTop: '1rem' }}>
            <button className="btn-primary">Start New Discovery</button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div data-testid="report-viewer">
      <div style={{ marginBottom: '1.5rem' }}>
        <Link to="/reports" style={{ fontSize: '0.875rem', color: 'var(--color-gray-600)' }}>← Back to Reports</Link>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginTop: '0.5rem' }}>Discovery Report</h2>
        <p style={{ color: 'var(--color-gray-600)', fontSize: '0.875rem' }}>
          Generated: {new Date(report.generatedAt).toLocaleString('en-AU')}
        </p>
      </div>

      {/* Disclaimer */}
      <div className="card" style={{ background: '#fef3c7', border: '1px solid #fcd34d', marginBottom: '1.5rem' }}>
        <p style={{ fontSize: '0.8rem', color: '#92400e' }}>
          ⚠️ <strong>Important Disclaimer:</strong> {report.disclaimer}
        </p>
      </div>

      {/* Executive Summary */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '0.75rem' }}>Executive Summary</h3>
        <p style={{ color: 'var(--color-gray-700)', lineHeight: 1.6, fontSize: '0.9rem' }}>{report.executiveSummary}</p>
      </div>

      {/* Ranked Shortlist */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '1rem' }}>Ranked Product Shortlist</h3>
        {report.rankedShortlist.length === 0 ? (
          <p style={{ color: 'var(--color-gray-600)' }}>No products were found matching your criteria.</p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {report.rankedShortlist.map((result: RecommendationResult) => (
              <div key={result.id} style={{
                border: '1px solid var(--color-gray-200)',
                borderRadius: 'var(--radius)',
                padding: '1rem',
                display: 'flex',
                gap: '1rem',
                alignItems: 'flex-start',
              }}>
                <div style={{
                  width: 40,
                  height: 40,
                  borderRadius: '50%',
                  background: 'var(--color-primary)',
                  color: 'white',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 700,
                  flexShrink: 0,
                }}>
                  #{result.rank}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                      <h4 style={{ fontWeight: 600 }}>{result.product.name}</h4>
                      <p style={{ color: 'var(--color-gray-600)', fontSize: '0.875rem' }}>{result.product.brandName}</p>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <p style={{ fontWeight: 700, color: 'var(--color-primary)', fontSize: '1.1rem' }}>
                        {(result.score * 100).toFixed(0)}
                      </p>
                      <p style={{ fontSize: '0.75rem', color: 'var(--color-gray-400)' }}>score</p>
                    </div>
                  </div>
                  <p style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: 'var(--color-gray-700)' }}>
                    {result.rationale}
                  </p>
                  {result.product.depositRates.length > 0 && (
                    <p style={{ marginTop: '0.5rem', fontSize: '0.875rem' }}>
                      <strong>Rate: </strong>
                      <span style={{ color: 'var(--color-success)' }}>
                        {(parseFloat(result.product.depositRates[0].rate) * 100).toFixed(2)}% p.a.
                      </span>
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Compliance Notes */}
      {report.complianceNotes.length > 0 && (
        <div className="card" style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '0.75rem' }}>Compliance Notes</h3>
          <ul style={{ paddingLeft: '1.5rem' }}>
            {report.complianceNotes.map((note, i) => (
              <li key={i} style={{ fontSize: '0.875rem', color: 'var(--color-gray-700)', marginBottom: '0.25rem' }}>{note}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Data warnings */}
      {report.missingDataWarnings.length > 0 && (
        <div className="card" style={{ background: '#fef3c7', border: '1px solid #fcd34d', marginBottom: '1.5rem' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.5rem', color: '#92400e' }}>Data Warnings</h3>
          <ul style={{ paddingLeft: '1.5rem' }}>
            {report.missingDataWarnings.map((w, i) => (
              <li key={i} style={{ fontSize: '0.8rem', color: '#92400e', marginBottom: '0.25rem' }}>{w}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
