import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { LoadingSpinner } from '../../components/ui/LoadingSpinner';

describe('LoadingSpinner', () => {
  it('renders default message', () => {
    render(<LoadingSpinner />);
    expect(screen.getByText('Loading...')).toBeInTheDocument();
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });

  it('renders custom message', () => {
    render(<LoadingSpinner message="Fetching products..." />);
    expect(screen.getByText('Fetching products...')).toBeInTheDocument();
  });
});
