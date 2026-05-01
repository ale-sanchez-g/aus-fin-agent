import { MOCK_PROVIDERS, MOCK_PRODUCTS } from './mock-data.js';

const USE_MOCK = process.env.USE_MOCK_DATA !== 'false';

let cdrModulePromise;
let adapterMode = USE_MOCK
  ? { source: 'mock_data', mockMode: true, reason: 'USE_MOCK_DATA enabled' }
  : { source: 'cdr_public', mockMode: false, reason: null };

function buildUnavailableReason(error) {
  return `open-banking-mcp unavailable${error?.message ? `: ${error.message}` : ''}`;
}

function buildUnavailableError(reason) {
  const error = new Error(reason);
  error.code = 'CDR_UNAVAILABLE';
  return error;
}

function resolveCdrApi(module) {
  if (!module || typeof module !== 'object') {
    throw new Error('open-banking-mcp did not export a module object');
  }

  const api = module.default && typeof module.default === 'object'
    ? module.default
    : module;

  if (typeof api.listDataHolders !== 'function') {
    throw new Error('open-banking-mcp API missing listDataHolders()');
  }

  if (typeof api.getProductsForHolder !== 'function') {
    throw new Error('open-banking-mcp API missing getProductsForHolder()');
  }

  if (typeof api.getProductDetail !== 'function') {
    throw new Error('open-banking-mcp API missing getProductDetail()');
  }

  return api;
}

async function getCdrModule() {
  if (USE_MOCK) return null;

  // Test-only switch: avoid importing open-banking-mcp when validating strict mode behavior.
  if (process.env.CDR_FORCE_UNAVAILABLE === 'true') {
    adapterMode = {
      source: 'cdr_unavailable',
      mockMode: false,
      reason: 'open-banking-mcp unavailable: forced by CDR_FORCE_UNAVAILABLE',
    };
    return null;
  }

  if (!cdrModulePromise) {
    cdrModulePromise = import('open-banking-mcp')
      .then((module) => {
        const api = resolveCdrApi(module);
        adapterMode = { source: 'cdr_public', mockMode: false, reason: null };
        return api;
      })
      .catch((error) => {
        const reason = buildUnavailableReason(error);
        adapterMode = {
          source: 'cdr_unavailable',
          mockMode: false,
          reason,
        };
        console.error(reason);
        return null;
      });
  }

  return cdrModulePromise;
}

export async function getAdapterStatus() {
  await getCdrModule();
  return adapterMode;
}

async function requireCdrModule() {
  const cdrModule = await getCdrModule();
  if (!cdrModule) {
    throw buildUnavailableError(adapterMode.reason || 'open-banking-mcp unavailable');
  }

  return cdrModule;
}

export async function listProviders() {
  if (USE_MOCK) return MOCK_PROVIDERS;

  const cdrModule = await requireCdrModule();
  const { listDataHolders } = cdrModule;
  return await listDataHolders();
}

export async function getProducts(providerId, category = null) {
  if (USE_MOCK) {
    const products = MOCK_PRODUCTS[providerId] || [];
    return category ? products.filter(p => p.productCategory === category) : products;
  }

  const cdrModule = await requireCdrModule();
  const { getProductsForHolder } = cdrModule;
  return await getProductsForHolder(providerId, { category });
}

export async function getProductDetail(providerId, productId) {
  if (USE_MOCK) {
    const products = MOCK_PRODUCTS[providerId] || [];
    return products.find(p => p.productId === productId) || null;
  }

  const cdrModule = await requireCdrModule();
  const { getProductDetail: cdrGetProduct } = cdrModule;
  return await cdrGetProduct(providerId, productId);
}
