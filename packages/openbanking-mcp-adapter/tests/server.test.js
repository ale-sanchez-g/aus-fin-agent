import { describe, it, before, after } from 'node:test';
import assert from 'node:assert/strict';

let serverInstance;
let baseUrl;

before(async () => {
  process.env.USE_MOCK_DATA = 'true';
  const { startServer } = await import(`../src/server.js?serverTest=${Date.now()}`);
  serverInstance = await startServer({ port: 0 });
  const address = serverInstance.address();
  const port = typeof address === 'object' && address ? address.port : 0;
  baseUrl = `http://localhost:${port}`;
});

after(async () => {
  if (serverInstance) {
    await new Promise((resolve, reject) => {
      serverInstance.close((err) => {
        if (err) return reject(err);
        resolve();
      });
    });
  }
});

describe('GET /health', () => {
  it('returns status ok', async () => {
    const res = await fetch(`${baseUrl}/health`);
    assert.equal(res.status, 200);
    const data = await res.json();
    assert.equal(data.status, 'ok');
    assert.equal(data.mockMode, true);
    assert.equal(data.source, 'mock_data');
  });
});

describe('GET /api/providers', () => {
  it('returns list of providers', async () => {
    const res = await fetch(`${baseUrl}/api/providers`);
    assert.equal(res.status, 200);
    const body = await res.json();
    assert.ok(Array.isArray(body.data));
    assert.ok(body.data.length >= 3);
    assert.ok(body.meta.total >= 3);
    assert.equal(body.meta.source, 'mock_data');
  });
});

describe('GET /api/providers/:id/products', () => {
  it('returns products for harbour-bank', async () => {
    const res = await fetch(`${baseUrl}/api/providers/harbour-bank/products`);
    assert.equal(res.status, 200);
    const body = await res.json();
    assert.ok(Array.isArray(body.data));
    assert.ok(body.data.length > 0);
    assert.equal(body.meta.provider_id, 'harbour-bank');
  });

  it('filters by category', async () => {
    const res = await fetch(`${baseUrl}/api/providers/harbour-bank/products?category=TRANS_AND_SAVINGS_ACCOUNTS`);
    assert.equal(res.status, 200);
    const body = await res.json();
    assert.ok(body.data.every(p => p.productCategory === 'TRANS_AND_SAVINGS_ACCOUNTS'));
  });
});

describe('GET /api/providers/:id/products/:productId', () => {
  it('returns product detail', async () => {
    const res = await fetch(`${baseUrl}/api/providers/harbour-bank/products/hb-everyday-savings`);
    assert.equal(res.status, 200);
    const body = await res.json();
    assert.equal(body.data.productId, 'hb-everyday-savings');
    assert.equal(body.data.productCategory, 'TRANS_AND_SAVINGS_ACCOUNTS');
  });

  it('returns 404 for unknown product', async () => {
    const res = await fetch(`${baseUrl}/api/providers/harbour-bank/products/nonexistent`);
    assert.equal(res.status, 404);
  });
});

describe('GET /api/products', () => {
  it('returns all products across providers', async () => {
    const res = await fetch(`${baseUrl}/api/products`);
    assert.equal(res.status, 200);
    const body = await res.json();
    assert.ok(Array.isArray(body.data));
    assert.ok(body.data.length > 5);  // We have 7 products total
  });

  it('filters all products by category', async () => {
    const res = await fetch(`${baseUrl}/api/products?category=TRANS_AND_SAVINGS_ACCOUNTS`);
    assert.equal(res.status, 200);
    const body = await res.json();
    assert.ok(body.data.every(p => p.productCategory === 'TRANS_AND_SAVINGS_ACCOUNTS'));
  });
});
