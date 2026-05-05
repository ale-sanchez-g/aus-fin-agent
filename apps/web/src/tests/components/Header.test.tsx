import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Header } from '../../components/layout/Header';

describe('Header', () => {
  it('renders', () => {
    render(<Header />);
    expect(screen.getByTestId('app-header')).toBeInTheDocument();
  });

  it('shows Public Data Mode badge', () => {
    render(<Header />);
    expect(screen.getByText(/Public Data Mode/i)).toBeInTheDocument();
  });
});
