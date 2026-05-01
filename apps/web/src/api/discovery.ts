import { apiClient } from './client';
import type { CreateDiscoveryRequest, DiscoverySession, RecommendationResult } from '../types';

export async function createSession(req: CreateDiscoveryRequest): Promise<DiscoverySession> {
  const res = await apiClient.post<DiscoverySession>('/discovery/sessions', req);
  return res.data;
}

export async function getSession(id: string): Promise<DiscoverySession> {
  const res = await apiClient.get<DiscoverySession>(`/discovery/sessions/${id}`);
  return res.data;
}

export async function getSessionResults(id: string): Promise<RecommendationResult[]> {
  const res = await apiClient.get<RecommendationResult[]>(`/discovery/sessions/${id}/results`);
  return res.data;
}

export async function listSessions(): Promise<DiscoverySession[]> {
  const res = await apiClient.get<DiscoverySession[]>('/discovery/sessions');
  return res.data;
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
