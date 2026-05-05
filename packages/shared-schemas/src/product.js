/**
 * CDR Product Categories
 * @readonly
 * @enum {string}
 */
export const ProductCategory = {
  TRANS_AND_SAVINGS_ACCOUNTS: 'TRANS_AND_SAVINGS_ACCOUNTS',
  TERM_DEPOSITS: 'TERM_DEPOSITS',
  TRAVEL_CARDS: 'TRAVEL_CARDS',
  REGULATED_TRUST_ACCOUNTS: 'REGULATED_TRUST_ACCOUNTS',
  RESIDENTIAL_MORTGAGES: 'RESIDENTIAL_MORTGAGES',
  CRED_AND_CHRG_CARDS: 'CRED_AND_CHRG_CARDS',
  PERS_LOANS: 'PERS_LOANS',
  LEASES: 'LEASES',
  MARGIN_LOANS: 'MARGIN_LOANS',
  OVERDRAFTS: 'OVERDRAFTS',
  BUSINESS_LOANS: 'BUSINESS_LOANS',
  TRADE_FINANCE: 'TRADE_FINANCE',
};

/**
 * @typedef {Object} ProductFeature
 * @property {string} featureType
 * @property {string} [additionalValue]
 * @property {string} [additionalInfo]
 */

/**
 * @typedef {Object} DepositRate
 * @property {string} depositRateType - CDR deposit rate type (BASE, BONUS, FIXED, etc.)
 * @property {string} rate - Rate as decimal string (e.g. "0.0475" for 4.75%)
 * @property {string} [comparisonRate]
 * @property {string} [calculationFrequency]
 * @property {string} [applicationFrequency]
 * @property {string} [additionalInfo]
 */

/**
 * @typedef {Object} LendingRate
 * @property {string} lendingRateType - CDR lending rate type (VARIABLE, FIXED, PURCHASE, etc.)
 * @property {string} rate - Rate as decimal string (e.g. "0.0624" for 6.24%)
 * @property {string} [comparisonRate]
 * @property {string} [calculationFrequency]
 * @property {string} [applicationFrequency]
 * @property {string} [additionalInfo]
 */

/**
 * @typedef {Object} ProductFee
 * @property {string} name
 * @property {string} feeType
 * @property {string} [amount]
 * @property {string} [balanceRate]
 * @property {string} [transactionRate]
 * @property {string} [additionalInfo]
 */

/**
 * @typedef {Object} EligibilityRule
 * @property {string} eligibilityType
 * @property {string} [additionalValue]
 * @property {string} [additionalInfo]
 */

/**
 * @typedef {Object} Product
 * @property {string} productId
 * @property {string} productCategory
 * @property {string} name
 * @property {string} [description]
 * @property {string} brand
 * @property {string} brandName
 * @property {string} [applicationUri]
 * @property {boolean} isTailored
 * @property {string} [effectiveFrom]
 * @property {string} [effectiveTo]
 * @property {string} lastUpdated
 * @property {ProductFeature[]} features
 * @property {ProductFee[]} fees
 * @property {DepositRate[]} depositRates
 * @property {LendingRate[]} lendingRates
 * @property {EligibilityRule[]} eligibility
 */
