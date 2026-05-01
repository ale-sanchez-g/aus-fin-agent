import React from 'react';

export function Header() {
  return (
    <header
      data-testid="app-header"
      style={{
        background: 'white',
        borderBottom: '1px solid var(--color-gray-200)',
        padding: '1rem 2rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        boxShadow: 'var(--shadow)',
      }}
    >
      <div />
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <span
          className="badge badge-info"
          title="Using public CDR product data. Consented data mode is disabled."
        >
          Public Data Mode
        </span>
        <div style={{
          width: 36,
          height: 36,
          borderRadius: '50%',
          background: 'var(--color-primary)',
          color: 'white',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '0.875rem',
          fontWeight: 600,
        }}>
          U
        </div>
      </div>
    </header>
  );
}
