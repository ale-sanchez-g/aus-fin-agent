import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { ReportViewer } from '../../pages/ReportViewer';

const baseProduct = {
  id: 'product-1',
  productId: 'product-1',
  productCategory: 'LEASES' as const,
  name: 'Finance Lease',
  brand: 'Test Bank',
  brandName: 'Test Bank',
  isTailored: false,
  features: [],
  fees: [],
  depositRates: [],
  lendingRates: [],
  eligibility: [],
};

const baseShortlistItem = {
  id: 'product-1',
  rank: 1,
  score: 55.5,
  rationale: 'Ranked #1 based on weighted suitability scoring.',
  scoreBreakdown: {
    monthlyFees: 60,
    rateCompetitiveness: 55,
    featureFit: 58,
    eligibilityFit: 57,
    digitalCapability: 50,
    suitability: 53,
    total: 55.5,
    weightProfile: 'balanced' as const,
  },
  product: baseProduct,
};

const baseReport = {
  sessionId: 'session-1',
  generatedAt: '2026-05-04T10:00:00.000Z',
  disclaimer: 'General information only.',
  executiveSummary: 'Summary',
  clientObjectives: 'Find best lease products',
  complianceNotes: [],
  missingDataWarnings: [],
  provenanceNotes: [],
  rankedShortlist: [baseShortlistItem],
};

const { getReport } = await import('../../api/reports');
vi.mock('../../api/reports', () => ({
  getReport: vi.fn(),
}));

function renderViewer() {
  return render(
    <MemoryRouter initialEntries={['/reports/session-1']}>
      <Routes>
        <Route path="/reports/:sessionId" element={<ReportViewer />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe('ReportViewer', () => {
  it('renders provider name and score percentage correctly', async () => {
    vi.mocked(getReport).mockResolvedValue(baseReport);
    renderViewer();

    await waitFor(() => {
      expect(screen.getByTestId('report-viewer')).toBeInTheDocument();
    });

    expect(screen.getByText('Test Bank')).toBeInTheDocument();
    expect(screen.getByText('55.50%')).toBeInTheDocument();
  });

  it('renders Apply Now link when applicationUri is present', async () => {
    vi.mocked(getReport).mockResolvedValue({
      ...baseReport,
      rankedShortlist: [
        {
          ...baseShortlistItem,
          product: {
            ...baseProduct,
            applicationUri: 'https://www.testbank.com.au/apply',
          },
        },
      ],
    });
    renderViewer();

    await waitFor(() => {
      expect(screen.getByTestId('report-viewer')).toBeInTheDocument();
    });

    const applyLink = screen.getByRole('link', { name: 'Apply Now' });
    expect(applyLink).toBeInTheDocument();
    expect(applyLink).toHaveAttribute('href', 'https://www.testbank.com.au/apply');
    expect(applyLink).toHaveAttribute('target', '_blank');
    expect(applyLink).toHaveAttribute('rel', 'noopener noreferrer');
  });

  it('does not render Apply Now link when applicationUri is absent', async () => {
    vi.mocked(getReport).mockResolvedValue(baseReport);
    renderViewer();

    await waitFor(() => {
      expect(screen.getByTestId('report-viewer')).toBeInTheDocument();
    });

    expect(screen.queryByRole('link', { name: 'Apply Now' })).not.toBeInTheDocument();
  });
});