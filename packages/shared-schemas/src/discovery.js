/**
 * Discovery request status values
 * @readonly
 * @enum {string}
 */
export const DiscoveryStatus = {
  PENDING: 'pending',
  IN_PROGRESS: 'in_progress',
  COMPLETED: 'completed',
  FAILED: 'failed',
};

/**
 * @typedef {Object} DiscoveryFilter
 * @property {string[]} [providerIds] - Filter to specific provider IDs
 * @property {string[]} [categories] - Filter to specific product categories
 * @property {number} [maxFeeAmount] - Maximum fee amount filter
 * @property {number} [minDepositRate] - Minimum deposit interest rate filter
 * @property {number} [maxLendingRate] - Maximum lending interest rate filter
 */

/**
 * @typedef {Object} DiscoveryRequest
 * @property {string} requestId - Unique identifier for this discovery request
 * @property {string} status - Current status of the discovery
 * @property {DiscoveryFilter} [filters] - Optional filters to apply
 * @property {string} createdAt - ISO 8601 timestamp when request was created
 * @property {string} [completedAt] - ISO 8601 timestamp when request completed
 */

/**
 * @typedef {Object} DiscoveryResult
 * @property {string} requestId
 * @property {import('./product.js').Product[]} products - Discovered products
 * @property {number} totalProducts - Total count of discovered products
 * @property {number} totalProviders - Number of providers queried
 * @property {string} timestamp - ISO 8601 timestamp of result
 */
