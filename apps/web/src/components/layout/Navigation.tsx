import React from 'react';
import { NavLink } from 'react-router-dom';

const NAV_ITEMS = [
  { path: '/', label: '📊 Dashboard', exact: true },
  { path: '/discover', label: '🔍 Discover' },
  { path: '/products', label: '📋 Products' },
  { path: '/reports', label: '📄 Reports' },
  { path: '/sync-status', label: '🔄 Sync Status' },
];

export function Navigation() {
  return (
    <nav
      role="navigation"
      aria-label="Main navigation"
      style={{
        width: 240,
        minHeight: '100vh',
        background: 'var(--color-primary)',
        padding: '1.5rem 0',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <div style={{ padding: '0 1.5rem 2rem', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
        <h1 style={{ color: 'white', fontSize: '1.125rem', fontWeight: 700 }}>
          AUS Fin Agent
        </h1>
        <p style={{ color: 'rgba(255,255,255,0.6)', fontSize: '0.75rem', marginTop: '0.25rem' }}>
          CDR Banking Platform
        </p>
      </div>
      <ul style={{ listStyle: 'none', marginTop: '1rem', flex: 1 }}>
        {NAV_ITEMS.map(item => (
          <li key={item.path}>
            <NavLink
              to={item.path}
              end={item.exact}
              style={({ isActive }) => ({
                display: 'block',
                padding: '0.75rem 1.5rem',
                color: isActive ? 'white' : 'rgba(255,255,255,0.7)',
                background: isActive ? 'rgba(255,255,255,0.15)' : 'transparent',
                fontWeight: isActive ? 600 : 400,
                fontSize: '0.875rem',
                borderLeft: isActive ? '3px solid white' : '3px solid transparent',
                transition: 'all 0.15s',
                textDecoration: 'none',
              })}
            >
              {item.label}
            </NavLink>
          </li>
        ))}
      </ul>
      <div style={{ padding: '1rem 1.5rem', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
        <p style={{ color: 'rgba(255,255,255,0.5)', fontSize: '0.7rem' }}>
          CDR Public Data Mode<br />v0.1.0
        </p>
      </div>
    </nav>
  );
}
