import express from 'express';
import { pathToFileURL } from 'url';
import { getAdapterStatus, listProviders, getProducts, getProductDetail } from './cdr-client.js';
import { requestLogger, errorHandler, correlationId } from './middleware.js';

const app = express();
const PORT = process.env.PORT || 4000;

app.use(express.json());
app.use(correlationId);
app.use(requestLogger);

// Health check
app.get('/health', async (req, res) => {
  const adapterStatus = await getAdapterStatus();
  res.json({
    status: 'ok',
    service: 'openbanking-mcp-adapter',
    version: '0.1.0',
    timestamp: new Date().toISOString(),
    mockMode: adapterStatus.mockMode,
    source: adapterStatus.source,
    reason: adapterStatus.reason,
  });
});

// List providers
app.get('/api/providers', async (req, res, next) => {
  try {
    const providers = await listProviders();
    const adapterStatus = await getAdapterStatus();
    res.json({ data: providers, meta: { total: providers.length, source: adapterStatus.source, timestamp: new Date().toISOString() } });
  } catch (err) { next(err); }
});

// List products for a provider
app.get('/api/providers/:providerId/products', async (req, res, next) => {
  try {
    const { providerId } = req.params;
    const { category } = req.query;
    const products = await getProducts(providerId, category);
    const adapterStatus = await getAdapterStatus();
    res.json({ data: products, meta: { total: products.length, source: adapterStatus.source, provider_id: providerId, timestamp: new Date().toISOString() } });
  } catch (err) { next(err); }
});

// Get product detail
app.get('/api/providers/:providerId/products/:productId', async (req, res, next) => {
  try {
    const { providerId, productId } = req.params;
    const product = await getProductDetail(providerId, productId);
    if (!product) return res.status(404).json({ error: 'Product not found' });
    const adapterStatus = await getAdapterStatus();
    res.json({ data: product, meta: { source: adapterStatus.source, timestamp: new Date().toISOString() } });
  } catch (err) { next(err); }
});

// List all products (across providers)
app.get('/api/products', async (req, res, next) => {
  try {
    const { category } = req.query;
    const providers = await listProviders();
    const allProducts = [];
    for (const provider of providers) {
      const products = await getProducts(provider.id, category);
      allProducts.push(...products);
    }
    const adapterStatus = await getAdapterStatus();
    res.json({ data: allProducts, meta: { total: allProducts.length, source: adapterStatus.source, timestamp: new Date().toISOString() } });
  } catch (err) { next(err); }
});

// Get product detail by productId only (searches across all providers)
app.get('/api/products/:productId', async (req, res, next) => {
  try {
    const { productId } = req.params;
    const providers = await listProviders();
    const adapterStatus = await getAdapterStatus();
    for (const provider of providers) {
      const product = await getProductDetail(provider.id, productId);
      if (product) {
        return res.json({ data: product, meta: { source: adapterStatus.source, timestamp: new Date().toISOString() } });
      }
    }
    return res.status(404).json({ error: 'Product not found' });
  } catch (err) { next(err); }
});

app.use(errorHandler);

async function startServer({ port = PORT } = {}) {
  const adapterStatus = await getAdapterStatus();
  if (!adapterStatus.mockMode && adapterStatus.source === 'cdr_unavailable') {
    throw new Error(adapterStatus.reason || 'open-banking-mcp unavailable');
  }

  return app.listen(port, () => {
    console.log(`openbanking-mcp-adapter listening on port ${port}`);
  });
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  await startServer();
}

export { app, startServer };
