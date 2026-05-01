/**
 * Report types for financial product analysis
 * @readonly
 * @enum {string}
 */
export const ReportType = {
  PRODUCT_COMPARISON: 'product_comparison',
  RATE_SUMMARY: 'rate_summary',
  FEE_ANALYSIS: 'fee_analysis',
  ELIGIBILITY_SUMMARY: 'eligibility_summary',
};

/**
 * @typedef {Object} RateSummary
 * @property {string} productId
 * @property {string} productName
 * @property {string} providerId
 * @property {string} providerName
 * @property {number} [bestDepositRate] - Highest available deposit rate as decimal
 * @property {number} [lowestLendingRate] - Lowest available lending rate as decimal
 * @property {string} productCategory
 */

/**
 * @typedef {Object} FeeSummary
 * @property {string} productId
 * @property {string} productName
 * @property {string} providerId
 * @property {string} providerName
 * @property {number} totalAnnualFees - Estimated total annual fees in AUD
 * @property {string[]} feeTypes - List of fee types applied
 */

/**
 * @typedef {Object} Report
 * @property {string} reportId - Unique identifier for this report
 * @property {ReportType} reportType - Type of report
 * @property {string} title - Human-readable report title
 * @property {string} generatedAt - ISO 8601 timestamp when report was generated
 * @property {RateSummary[]|FeeSummary[]} items - Report line items
 * @property {Object} [summary] - Aggregate summary statistics
 * @property {number} [summary.totalProducts] - Total products analysed
 * @property {number} [summary.totalProviders] - Total providers analysed
 */
