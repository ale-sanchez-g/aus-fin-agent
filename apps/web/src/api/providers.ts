import { apiClient } from './client';
import type { Provider, SyncJob } from '../types';

export async function listProviders(): Promise<Provider[]> {
  const res = await apiClient.get<Provider[]>('/providers');
  return res.data;
}

export async function getSyncStatus(providerId: string): Promise<SyncJob> {
  const res = await apiClient.get<SyncJob>(`/providers/${providerId}/sync-status`);
  return res.data;
}

export async function triggerSync(providerId: string): Promise<SyncJob> {
  const res = await apiClient.post<SyncJob>(`/providers/${providerId}/sync`);
  return res.data;
}
