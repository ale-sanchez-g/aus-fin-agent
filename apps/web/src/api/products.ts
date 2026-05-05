import { apiClient } from './client';
import type { Product, PaginatedResponse, ProductCategory } from '../types';

export interface ProductListParams {
  page?: number;
  pageSize?: number;
  category?: ProductCategory;
  providerId?: string;
  search?: string;
}

export interface IntentSearchResult {
  products: Product[];
  inferredCategory: string;
  inferredProfile: string;
  userIntent: string;
  total: number;
}

export async function listProducts(params: ProductListParams = {}): Promise<PaginatedResponse<Product>> {
  const res = await apiClient.get<PaginatedResponse<Product>>('/products', { params });
  return res.data;
}

export async function getProduct(id: string): Promise<Product> {
  const res = await apiClient.get<Product>(`/products/${id}`);
  return res.data;
}

export async function compareProducts(ids: string[]): Promise<Product[]> {
  const res = await apiClient.get<Product[]>('/products/compare', { params: { ids: ids.join(',') } });
  return res.data;
}

export async function searchProductsByIntent(
  userIntent: string,
  maxResults = 6,
): Promise<IntentSearchResult> {
  // MCP calls can take up to 20s per bank — use a generous timeout
  const res = await apiClient.post<IntentSearchResult>(
    '/products/search-by-intent',
    { user_intent: userIntent, max_results: maxResults },
    { timeout: 120_000 },
  );
  return res.data;
}
