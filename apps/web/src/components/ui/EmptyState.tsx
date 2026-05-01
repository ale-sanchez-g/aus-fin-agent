import React from 'react';

interface Props {
  title: string;
  description?: string;
  action?: React.ReactNode;
}

export function EmptyState({ title, description, action }: Props) {
  return (
    <div
      data-testid="empty-state"
      style={{
        textAlign: 'center',
        padding: '4rem 2rem',
        color: 'var(--color-gray-600)',
      }}
    >
      <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📭</div>
      <h3 style={{ marginBottom: '0.5rem', color: 'var(--color-gray-800)' }}>{title}</h3>
      {description && <p style={{ marginBottom: '1.5rem' }}>{description}</p>}
      {action}
    </div>
  );
}
