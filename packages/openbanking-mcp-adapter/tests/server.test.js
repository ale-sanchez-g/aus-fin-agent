import { describe, it, before, after } from 'node:test';
import assert from 'node:assert/strict';

// Set mock mode before importing server
process.env.USE_MOCK_DATA = 'true';
process.env.PORT = '4001';  // Use different port for tests

const BASE_URL = 'http://localhost:4001';
let serverInstance;

before(async () => {
  const { server } = await import('../src/server.js');
  serverInstance = server;
  await new Promise(resolve => setTimeout(resolve, 200));
});

after(() => {
  serverInstance?.close();
});

describe('GET /health', () => {
  it('returns status ok', async () => {
    const res = await fetch(`${BASE_URL}/health`);
    assert.equal(res.status, 200);
    const data = await res.json();
    assert.equal(data.status, 'ok');
    assert.equal(data.mockMode, true);
  });
});

describe('GET /api/providers', () => {
  it('returns list of providers', async () => {
    const res = await fetch(`${BASE_URL}/api/providers`);
    assert.equal(res.status, 200);
    const body = await res.json();
    assert.ok(Array.isArray(body.data));
    assert.ok(body.data.length >= 3);
    assert.ok(body.meta.total >= 3);
    assert.equal(body.meta.source, 'cdr_public');
  });
});

describe('GET /api/providers/:id/products', () => {
  it('returns products for harbour-bank', async () => {
    const res = await fetch(`${BASE_URL}/api/providers/harbour-bank/products`);
    assert.equal(res.status, 200);
    const body = await res.json();
    assert.ok(Array.isArray(body.data));
    assert.ok(body.data.length > 0);
    assert.equal(body.meta.provider_id, 'harbour-bank');
  });

  it('filters by category', async () => {
    const res = await fetch(`${BASE_URL}/api/providers/harbour-bank/products?category=TRANS_AND_SAVINGS_ACCOUNTS`);
    assert.equal(res.status, 200);
    const body = await res.json();
    assert.ok(body.data.every(p => p.productCategory === 'TRANS_AND_SAVINGS_ACCOUNTS'));
  });
});

describe('GET /api/providers/:id/products/:productId', () => {
  it('returns product detail', async () => {
    const res = await fetch(`${BASE_URL}/api/providers/harbour-bank/products/hb-everyday-savings`);
    assert.equal(res.status, 200);
    const body = await res.json();
    assert.equal(body.data.productId, 'hb-everyday-savings');
    assert.equal(body.data.productCategory, 'TRANS_AND_SAVINGS_ACCOUNTS');
  });

  it('returns 404 for unknown product', async () => {
    const res = await fetch(`${BASE_URL}/api/providers/harbour-bank/products/nonexistent`);
    assert.equal(res.status, 404);
  });
});

describe('GET /api/products', () => {
  it('returns all products across providers', async () => {
    const res = await fetch(`${BASE_URL}/api/products`);
    assert.equal(res.status, 200);
    const body = await res.json();
    assert.ok(Array.isArray(body.data));
    assert.ok(body.data.length > 5);  // We have 7 products total
  });

  it('filters all products by category', async () => {
    const res = await fetch(`${BASE_URL}/api/products?category=TRANS_AND_SAVINGS_ACCOUNTS`);
    assert.equal(res.status, 200);
    const body = await res.json();
    assert.ok(body.data.every(p => p.productCategory === 'TRANS_AND_SAVINGS_ACCOUNTS'));
  });
});
