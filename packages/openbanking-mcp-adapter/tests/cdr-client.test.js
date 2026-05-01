import { describe, it } from 'node:test';
import assert from 'node:assert/strict';

describe('cdr-client strict mode', () => {
  it('does not fall back to mock data when real mode is enabled', async () => {
    const previousUseMock = process.env.USE_MOCK_DATA;
    const previousForceUnavailable = process.env.CDR_FORCE_UNAVAILABLE;
    try {
      process.env.USE_MOCK_DATA = 'false';
      process.env.CDR_FORCE_UNAVAILABLE = 'true';

      const module = await import(`../src/cdr-client.js?strict=${Date.now()}`);
      const status = await module.getAdapterStatus();

      assert.equal(status.mockMode, false);
      assert.equal(status.source, 'cdr_unavailable');
      assert.match(status.reason, /open-banking-mcp unavailable/);
      await assert.rejects(() => module.listProviders(), /open-banking-mcp unavailable/);
    } finally {
      if (previousUseMock === undefined) {
        delete process.env.USE_MOCK_DATA;
      } else {
        process.env.USE_MOCK_DATA = previousUseMock;
      }

      if (previousForceUnavailable === undefined) {
        delete process.env.CDR_FORCE_UNAVAILABLE;
      } else {
        process.env.CDR_FORCE_UNAVAILABLE = previousForceUnavailable;
      }
    }
  });
});