import { apiClient } from './client';
import type { Product, PaginatedResponse, ProductCategory } from '../types';

export interface ProductListParams {
  page?: number;
  pageSize?: number;
  category?: ProductCategory;
  providerId?: string;
  search?: string;
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
