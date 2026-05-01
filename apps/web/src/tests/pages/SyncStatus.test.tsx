import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { SyncStatus } from '../../pages/SyncStatus';

vi.mock('../../api/providers', () => ({
  listProviders: vi.fn().mockResolvedValue([]),
}));

describe('SyncStatus', () => {
  it('renders sync status page', async () => {
    render(<MemoryRouter><SyncStatus /></MemoryRouter>);
    await waitFor(() => {
      expect(screen.getByTestId('sync-status')).toBeInTheDocument();
    });
  });

  it('shows provider table headers', async () => {
    render(<MemoryRouter><SyncStatus /></MemoryRouter>);
    await waitFor(() => {
      expect(screen.getByText('Provider')).toBeInTheDocument();
      expect(screen.getByText('Status')).toBeInTheDocument();
    });
  });
});
