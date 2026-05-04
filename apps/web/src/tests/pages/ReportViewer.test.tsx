import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { ReportViewer } from '../../pages/ReportViewer';

vi.mock('../../api/reports', () => ({
  getReport: vi.fn().mockResolvedValue({
    sessionId: 'session-1',
    generatedAt: '2026-05-04T10:00:00.000Z',
    disclaimer: 'General information only.',
    executiveSummary: 'Summary',
    clientObjectives: 'Find best lease products',
    complianceNotes: [],
    missingDataWarnings: [],
    provenanceNotes: [],
    rankedShortlist: [
      {
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
          weightProfile: 'balanced',
        },
        product: {
          id: 'product-1',
          productId: 'product-1',
          productCategory: 'LEASES',
          name: 'Finance Lease',
          brand: 'Test Bank',
          brandName: 'Test Bank',
          isTailored: false,
          features: [],
          fees: [],
          depositRates: [],
          lendingRates: [],
          eligibility: [],
        },
      },
    ],
  }),
}));

describe('ReportViewer', () => {
  it('renders provider name and score percentage correctly', async () => {
    render(
      <MemoryRouter initialEntries={['/reports/session-1']}>
        <Routes>
          <Route path="/reports/:sessionId" element={<ReportViewer />} />
        </Routes>
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(screen.getByTestId('report-viewer')).toBeInTheDocument();
    });

    expect(screen.getByText('Test Bank')).toBeInTheDocument();
    expect(screen.getByText('55.50%')).toBeInTheDocument();
  });
});