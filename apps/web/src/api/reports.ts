import { apiClient } from './client';
import type { DiscoveryReport } from '../types';

export async function getReport(sessionId: string): Promise<DiscoveryReport> {
  const res = await apiClient.get<DiscoveryReport>(`/reports/${sessionId}`);
  return res.data;
}
