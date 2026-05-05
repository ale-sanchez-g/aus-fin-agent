import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { ReportsList } from '../../pages/ReportsList';
import { listSessions } from '../../api/discovery';

vi.mock('../../api/discovery', () => ({
  listSessions: vi.fn(),
}));

const listSessionsMock = vi.mocked(listSessions);

describe('ReportsList', () => {
  beforeEach(() => {
    listSessionsMock.mockReset();
  });

  it('renders completed reports with links', async () => {
    listSessionsMock.mockResolvedValue([
      {
        id: 'session-completed-1',
        status: 'completed',
        productCategory: 'TERM_DEPOSITS',
        weightProfile: 'balanced',
        createdAt: '2026-05-01T10:00:00.000Z',
        completedAt: '2026-05-01T10:02:00.000Z',
      },
      {
        id: 'session-running-1',
        status: 'running',
        productCategory: 'PERS_LOANS',
        weightProfile: 'balanced',
        createdAt: '2026-05-01T10:03:00.000Z',
      },
    ]);

    render(
      <MemoryRouter>
        <ReportsList />
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(screen.getByTestId('reports-list')).toBeInTheDocument();
    });

    expect(screen.getByText('session-completed-1')).toBeInTheDocument();
    expect(screen.getByText('Term Deposits')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /View report/i })).toHaveAttribute('href', '/reports/session-completed-1');
    expect(screen.queryByText('session-running-1')).not.toBeInTheDocument();
  });

  it('shows empty state when there are no completed reports', async () => {
    listSessionsMock.mockResolvedValue([
      {
        id: 'session-pending-1',
        status: 'pending',
        productCategory: 'PERS_LOANS',
        weightProfile: 'balanced',
        createdAt: '2026-05-01T10:00:00.000Z',
      },
    ]);

    render(
      <MemoryRouter>
        <ReportsList />
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(screen.getByText(/No completed reports yet/i)).toBeInTheDocument();
    });
    expect(screen.getByRole('button', { name: /Start Discovery/i })).toBeInTheDocument();
  });
});