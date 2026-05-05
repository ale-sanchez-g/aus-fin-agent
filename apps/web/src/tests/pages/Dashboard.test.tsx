import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { Dashboard } from '../../pages/Dashboard';

// Mock the API modules
vi.mock('../../api/discovery', () => ({
  listSessions: vi.fn().mockResolvedValue([]),
}));
vi.mock('../../api/providers', () => ({
  listProviders: vi.fn().mockResolvedValue([]),
}));

describe('Dashboard', () => {
  it('renders dashboard heading', async () => {
    render(<MemoryRouter><Dashboard /></MemoryRouter>);
    await waitFor(() => {
      expect(screen.getByTestId('dashboard')).toBeInTheDocument();
    });
  });

  it('shows CDR notice', async () => {
    render(<MemoryRouter><Dashboard /></MemoryRouter>);
    await waitFor(() => {
      expect(screen.getByText(/CDR Public Data Mode/i)).toBeInTheDocument();
    });
  });

  it('shows start discovery button', async () => {
    render(<MemoryRouter><Dashboard /></MemoryRouter>);
    await waitFor(() => {
      expect(screen.getByText(/Start Discovery/i)).toBeInTheDocument();
    });
  });
});
