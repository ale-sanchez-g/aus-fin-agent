import React from 'react';
import { Link } from 'react-router-dom';

export function NotFound() {
  return (
    <div style={{ textAlign: 'center', padding: '4rem' }}>
      <div style={{ fontSize: '4rem' }}>404</div>
      <h2 style={{ marginTop: '1rem' }}>Page Not Found</h2>
      <p style={{ color: 'var(--color-gray-600)', margin: '1rem 0' }}>
        The page you are looking for does not exist.
      </p>
      <Link to="/">
        <button className="btn-primary">← Back to Dashboard</button>
      </Link>
    </div>
  );
}
