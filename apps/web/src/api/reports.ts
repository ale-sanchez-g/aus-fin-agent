import { apiClient } from './client';
import type { DiscoveryReport } from '../types';
import type { WeightProfile } from '../types';

type ReportArtifactResponse = {
  id: string;
  session_id: string;
  content?: BackendDiscoveryReport;
};

type BackendDiscoveryReport = {
  session_id: string;
  generated_at: string;
  product_category?: string;
  top_recommendations?: Array<{
    rank?: number;
    product_id?: string;
    external_product_id?: string;
    name?: string;
    category?: string;
    total_score?: number;
    score_breakdown?: Record<string, number | string>;
    rates?: Array<Record<string, string>>;
    fees?: Array<Record<string, string>>;
    features?: Array<Record<string, string>>;
    application_uri?: string;
  }>;
  narrative?: string;
  compliance_notes?: string[];
  disclaimer?: string;
};

function mapBackendReport(input: BackendDiscoveryReport): DiscoveryReport {
  const shortlist = (input.top_recommendations ?? []).map((item, index) => {
    const scoreBreakdown = item.score_breakdown ?? {};
    const rateRows = item.rates ?? [];
    return {
      id: item.product_id ?? item.external_product_id ?? `product-${index + 1}`,
      rank: item.rank ?? index + 1,
      score: Number(item.total_score ?? 0),
      scoreBreakdown: {
        monthlyFees: Number(scoreBreakdown.monthly_fees ?? 0),
        rateCompetitiveness: Number(scoreBreakdown.rate_competitiveness ?? 0),
        featureFit: Number(scoreBreakdown.feature_fit ?? 0),
        eligibilityFit: Number(scoreBreakdown.eligibility_fit ?? 0),
        digitalCapability: Number(scoreBreakdown.digital_capability ?? 0),
        suitability: Number(scoreBreakdown.suitability ?? 0),
        total: Number(scoreBreakdown.total ?? item.total_score ?? 0),
        weightProfile: 'balanced' as WeightProfile,
      },
      rationale: `Ranked #${item.rank ?? index + 1} based on weighted suitability scoring.`,
      product: {
        id: item.product_id ?? item.external_product_id ?? `product-${index + 1}`,
        productId: item.external_product_id ?? item.product_id ?? `product-${index + 1}`,
        productCategory: (item.category ?? input.product_category ?? 'TRANS_AND_SAVINGS_ACCOUNTS') as DiscoveryReport['rankedShortlist'][number]['product']['productCategory'],
        name: item.name ?? 'Unknown product',
        brand: 'Unknown',
        brandName: 'Unknown provider',
        applicationUri: item.application_uri,
        isTailored: false,
        features: (item.features ?? []).map((feature) => ({
          featureType: feature.feature_type ?? feature.type ?? 'feature',
          additionalValue: feature.additional_value,
          additionalInfo: feature.additional_info,
        })),
        fees: (item.fees ?? []).map((fee) => ({
          name: fee.name ?? fee.fee_name ?? 'Fee',
          feeType: fee.fee_type ?? fee.type ?? 'UNKNOWN',
          amount: fee.amount,
          additionalInfo: fee.additional_info,
        })),
        depositRates: rateRows.map((rate) => ({
          rateType: rate.rate_type ?? rate.type ?? 'standard',
          rate: rate.rate ?? '0',
          comparisonRate: rate.comparison_rate,
          calculationFrequency: rate.calculation_frequency,
          applicationFrequency: rate.application_frequency,
          additionalInfo: rate.additional_info,
        })),
        lendingRates: [],
        eligibility: [],
      },
    };
  });

  return {
    sessionId: input.session_id,
    generatedAt: input.generated_at,
    disclaimer: input.disclaimer ?? 'General information only. Not financial advice.',
    executiveSummary: input.narrative ?? 'Product ranking completed based on the selected profile.',
    clientObjectives: input.product_category ?? 'Not specified',
    rankedShortlist: shortlist,
    complianceNotes: input.compliance_notes ?? [],
    missingDataWarnings: [],
    provenanceNotes: [],
  };
}

export async function getReport(sessionId: string): Promise<DiscoveryReport> {
  const res = await apiClient.get<DiscoveryReport | ReportArtifactResponse>(`/reports/${sessionId}`);
  const payload = res.data as DiscoveryReport | ReportArtifactResponse;

  if ('rankedShortlist' in payload) {
    return payload;
  }

  if (payload.content) {
    return mapBackendReport(payload.content);
  }

  throw new Error('Report payload is missing content');
}
