import { MOCK_PROVIDERS, MOCK_PRODUCTS } from './mock-data.js';

const USE_MOCK = process.env.USE_MOCK_DATA !== 'false';

export async function listProviders() {
  if (USE_MOCK) return MOCK_PROVIDERS;
  // In production: call open-banking-mcp or CDR API
  try {
    const { listDataHolders } = await import('open-banking-mcp');
    return await listDataHolders();
  } catch {
    console.warn('open-banking-mcp unavailable, using mock data');
    return MOCK_PROVIDERS;
  }
}

export async function getProducts(providerId, category = null) {
  if (USE_MOCK) {
    const products = MOCK_PRODUCTS[providerId] || [];
    return category ? products.filter(p => p.productCategory === category) : products;
  }
  try {
    const { getProductsForHolder } = await import('open-banking-mcp');
    const products = await getProductsForHolder(providerId, { category });
    return products;
  } catch {
    console.warn('open-banking-mcp unavailable, using mock data');
    const products = MOCK_PRODUCTS[providerId] || [];
    return category ? products.filter(p => p.productCategory === category) : products;
  }
}

export async function getProductDetail(providerId, productId) {
  if (USE_MOCK) {
    const products = MOCK_PRODUCTS[providerId] || [];
    return products.find(p => p.productId === productId) || null;
  }
  try {
    const { getProductDetail: cdrGetProduct } = await import('open-banking-mcp');
    return await cdrGetProduct(providerId, productId);
  } catch {
    console.warn('open-banking-mcp unavailable, using mock data');
    const products = MOCK_PRODUCTS[providerId] || [];
    return products.find(p => p.productId === productId) || null;
  }
}
