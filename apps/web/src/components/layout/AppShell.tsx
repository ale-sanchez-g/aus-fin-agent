import React from 'react';
import { Outlet } from 'react-router-dom';
import { Navigation } from './Navigation';
import { Header } from './Header';

export function AppShell() {
  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <Navigation />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <Header />
        <main style={{ flex: 1, padding: '2rem', overflowY: 'auto' }}>
          <Outlet />
        </main>
        <footer style={{
          borderTop: '1px solid var(--color-gray-200)',
          padding: '1rem 2rem',
          fontSize: '0.75rem',
          color: 'var(--color-gray-400)',
          background: 'white',
        }}>
          <p>
            ⚠️ <strong>Disclaimer:</strong> This platform provides product discovery support only.
            Information is sourced from Australian CDR public product data and does not constitute
            personal financial advice. Always consult a licensed financial adviser before making
            financial decisions. Data is provided "as is" and may not reflect current offers.
          </p>
        </footer>
      </div>
    </div>
  );
}
