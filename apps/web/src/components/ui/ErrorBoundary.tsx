import React, { Component, ReactNode } from 'react';

interface Props { children: ReactNode }
interface State { hasError: boolean; error?: Error }

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }
  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '2rem', textAlign: 'center' }}>
          <h2 style={{ color: 'var(--color-error)' }}>Something went wrong</h2>
          <p style={{ color: 'var(--color-gray-600)', marginTop: '0.5rem' }}>
            {this.state.error?.message}
          </p>
          <button
            className="btn-primary"
            style={{ marginTop: '1rem' }}
            onClick={() => this.setState({ hasError: false })}
          >
            Try Again
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
