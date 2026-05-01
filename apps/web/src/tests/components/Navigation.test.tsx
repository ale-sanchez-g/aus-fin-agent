import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { Navigation } from '../../components/layout/Navigation';

describe('Navigation', () => {
  it('renders all nav items', () => {
    render(<MemoryRouter><Navigation /></MemoryRouter>);
    expect(screen.getByText(/Dashboard/i)).toBeInTheDocument();
    expect(screen.getAllByText(/Discover/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/Products/i)).toBeInTheDocument();
    expect(screen.getByText(/Sync Status/i)).toBeInTheDocument();
  });

  it('renders brand name', () => {
    render(<MemoryRouter><Navigation /></MemoryRouter>);
    expect(screen.getByText(/AUS Fin Agent/i)).toBeInTheDocument();
  });

  it('has navigation role', () => {
    render(<MemoryRouter><Navigation /></MemoryRouter>);
    expect(screen.getByRole('navigation')).toBeInTheDocument();
  });
});
