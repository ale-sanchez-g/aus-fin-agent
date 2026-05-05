/**
 * Provider industry types supported by CDR
 * @readonly
 * @enum {string}
 */
export const ProviderIndustry = {
  BANKING: 'banking',
  ENERGY: 'energy',
  TELCO: 'telco',
};

/**
 * @typedef {Object} Provider
 * @property {string} id - Unique identifier for the provider
 * @property {string} name - Full legal name of the provider
 * @property {string} [abn] - Australian Business Number
 * @property {string} brandName - Brand name displayed to consumers
 * @property {string} industry - Industry sector (banking, energy, telco)
 * @property {string} [logoUri] - URL to the provider's logo
 * @property {string} [websiteUri] - URL to the provider's website
 * @property {string} [cdrHolderId] - CDR register holder identifier
 */

/**
 * @typedef {Object} ProviderListMeta
 * @property {number} total - Total number of providers
 * @property {string} source - Data source identifier
 * @property {string} timestamp - ISO 8601 timestamp of response
 */

/**
 * @typedef {Object} ProviderListResponse
 * @property {Provider[]} data
 * @property {ProviderListMeta} meta
 */
