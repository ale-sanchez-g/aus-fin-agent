export type ProductCategory =
  | 'TRANS_AND_SAVINGS_ACCOUNTS'
  | 'TERM_DEPOSITS'
  | 'TRAVEL_CARDS'
  | 'REGULATED_TRUST_ACCOUNTS'
  | 'RESIDENTIAL_MORTGAGES'
  | 'CRED_AND_CHRG_CARDS'
  | 'PERS_LOANS'
  | 'LEASES'
  | 'MARGIN_LOANS'
  | 'OVERDRAFTS'
  | 'BUSINESS_LOANS'
  | 'TRADE_FINANCE';

export const PRODUCT_CATEGORY_LABELS: Record<ProductCategory, string> = {
  TRANS_AND_SAVINGS_ACCOUNTS: 'Transaction & Savings',
  TERM_DEPOSITS: 'Term Deposits',
  TRAVEL_CARDS: 'Travel Cards',
  REGULATED_TRUST_ACCOUNTS: 'Regulated Trust Accounts',
  RESIDENTIAL_MORTGAGES: 'Home Loans',
  CRED_AND_CHRG_CARDS: 'Credit & Charge Cards',
  PERS_LOANS: 'Personal Loans',
  LEASES: 'Leases',
  MARGIN_LOANS: 'Margin Loans',
  OVERDRAFTS: 'Overdrafts',
  BUSINESS_LOANS: 'Business Loans',
  TRADE_FINANCE: 'Trade Finance',
};

export interface Provider {
  id: string;
  name: string;
  brandName: string;
  abn?: string;
  logoUri?: string;
  websiteUri?: string;
  isActive: boolean;
  lastSyncAt?: string;
}

export interface ProductFeature {
  featureType: string;
  additionalValue?: string;
  additionalInfo?: string;
}

export interface ProductRate {
  rateType: string;
  rate: string;
  comparisonRate?: string;
  calculationFrequency?: string;
  applicationFrequency?: string;
  additionalInfo?: string;
}

export interface ProductFee {
  name: string;
  feeType: string;
  amount?: string;
  additionalInfo?: string;
}

export interface EligibilityRule {
  eligibilityType: string;
  additionalValue?: string;
  additionalInfo?: string;
}

export interface Product {
  id: string;
  productId: string;
  productCategory: ProductCategory;
  name: string;
  description?: string;
  brand: string;
  brandName: string;
  applicationUri?: string;
  isTailored: boolean;
  effectiveFrom?: string;
  effectiveTo?: string;
  lastUpdated?: string;
  features: ProductFeature[];
  fees: ProductFee[];
  depositRates: ProductRate[];
  lendingRates: ProductRate[];
  eligibility: EligibilityRule[];
  providerId?: string;
}

export type WeightProfile = 'balanced' | 'fee_conscious' | 'rate_focused' | 'feature_rich';

export interface ClientPreferences {
  maxMonthlyFee?: number;
  targetRate?: number;
  requiredFeatures?: string[];
  minCreditLimit?: number;
  maxLoanAmount?: number;
}

export interface CreateDiscoveryRequest {
  userIntent: string;
  productCategory: ProductCategory;
  preferences: ClientPreferences;
  constraints: ClientPreferences;
  weightProfile: WeightProfile;
}

export type SessionStatus = 'pending' | 'running' | 'completed' | 'failed';

export interface DiscoverySession {
  id: string;
  status: SessionStatus;
  productCategory: ProductCategory;
  weightProfile: WeightProfile;
  userIntent?: string;
  createdAt: string;
  completedAt?: string;
  errorMessage?: string;
}

export interface ScoreBreakdown {
  monthlyFees: number;
  rateCompetitiveness: number;
  featureFit: number;
  eligibilityFit: number;
  digitalCapability: number;
  suitability: number;
  total: number;
  weightProfile: WeightProfile;
}

export interface RecommendationResult {
  id: string;
  rank: number;
  score: number;
  scoreBreakdown: ScoreBreakdown;
  rationale: string;
  product: Product;
}

export interface ReportSection {
  title: string;
  content: string;
}

export interface DiscoveryReport {
  sessionId: string;
  generatedAt: string;
  disclaimer: string;
  executiveSummary: string;
  clientObjectives: string;
  rankedShortlist: RecommendationResult[];
  complianceNotes: string[];
  missingDataWarnings: string[];
  provenanceNotes: string[];
}

export interface SyncJob {
  id: string;
  providerId: string;
  providerName: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  startedAt?: string;
  completedAt?: string;
  recordsProcessed?: number;
  errorMessage?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
}

export interface ApiError {
  detail: string;
  status: number;
}
