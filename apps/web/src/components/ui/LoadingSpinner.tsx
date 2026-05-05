import React from 'react';

interface Props { message?: string }

export function LoadingSpinner({ message = 'Loading...' }: Props) {
  return (
    <div
      data-testid="loading-spinner"
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '3rem',
        gap: '1rem',
        color: 'var(--color-gray-600)',
      }}
    >
      <div style={{
        width: 40,
        height: 40,
        border: '3px solid var(--color-gray-200)',
        borderTopColor: 'var(--color-primary)',
        borderRadius: '50%',
        animation: 'spin 0.8s linear infinite',
      }} />
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      <p>{message}</p>
    </div>
  );
}
