import { apiClient } from './client';
import type { CreateDiscoveryRequest, DiscoverySession, RecommendationResult } from '../types';

type RawSession = {
  id: string;
  status: string;
  product_category?: string;
  weight_profile?: string;
  user_intent?: string;
  created_at?: string;
  completed_at?: string;
  error_message?: string;
  // camelCase variants (in case backend ever switches)
  productCategory?: string;
  weightProfile?: string;
  userIntent?: string;
  createdAt?: string;
  completedAt?: string;
  errorMessage?: string;
};

function mapSession(raw: RawSession): DiscoverySession {
  return {
    id: raw.id,
    status: raw.status as DiscoverySession['status'],
    productCategory: (raw.product_category ?? raw.productCategory ?? 'TRANS_AND_SAVINGS_ACCOUNTS') as DiscoverySession['productCategory'],
    weightProfile: (raw.weight_profile ?? raw.weightProfile ?? 'balanced') as DiscoverySession['weightProfile'],
    userIntent: raw.user_intent ?? raw.userIntent,
    createdAt: raw.created_at ?? raw.createdAt ?? new Date().toISOString(),
    completedAt: raw.completed_at ?? raw.completedAt,
    errorMessage: raw.error_message ?? raw.errorMessage,
  };
}

export async function createSession(req: CreateDiscoveryRequest): Promise<DiscoverySession> {
  const res = await apiClient.post<RawSession>('/discovery/sessions', req);
  return mapSession(res.data);
}

export async function getSession(id: string): Promise<DiscoverySession> {
  const res = await apiClient.get<RawSession>(`/discovery/sessions/${id}`);
  return mapSession(res.data);
}

export async function getSessionResults(id: string): Promise<RecommendationResult[]> {
  const res = await apiClient.get<RecommendationResult[]>(`/discovery/sessions/${id}/results`);
  return res.data;
}

export async function listSessions(): Promise<DiscoverySession[]> {
  const res = await apiClient.get<RawSession[]>('/discovery/sessions');
  return res.data.map(mapSession);
}

export async function pollSession(id: string, maxWaitMs = 120000): Promise<DiscoverySession> {
  const start = Date.now();
  while (Date.now() - start < maxWaitMs) {
    const session = await getSession(id);
    if (session.status === 'completed' || session.status === 'failed') return session;
    await new Promise(r => setTimeout(r, 2000));
  }
  throw new Error('Session polling timed out');
}
