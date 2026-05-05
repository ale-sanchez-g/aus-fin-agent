import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { EmptyState } from '../../components/ui/EmptyState';

describe('EmptyState', () => {
  it('renders title', () => {
    render(<EmptyState title="No products found" />);
    expect(screen.getByText('No products found')).toBeInTheDocument();
  });

  it('renders description when provided', () => {
    render(<EmptyState title="No results" description="Try different filters" />);
    expect(screen.getByText('Try different filters')).toBeInTheDocument();
  });

  it('renders action when provided', () => {
    render(<EmptyState title="Empty" action={<button>Reset</button>} />);
    expect(screen.getByText('Reset')).toBeInTheDocument();
  });
});
