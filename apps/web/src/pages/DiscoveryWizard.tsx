import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createSession, pollSession } from '../api/discovery';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import type { ProductCategory, WeightProfile, ClientPreferences } from '../types';
import { PRODUCT_CATEGORY_LABELS } from '../types';

const CATEGORY_ICONS: Record<ProductCategory, string> = {
  TRANS_AND_SAVINGS_ACCOUNTS: '💰',
  TERM_DEPOSITS: '🏦',
  TRAVEL_CARDS: '✈️',
  REGULATED_TRUST_ACCOUNTS: '⚖️',
  RESIDENTIAL_MORTGAGES: '🏠',
  CRED_AND_CHRG_CARDS: '💳',
  PERS_LOANS: '👤',
  LEASES: '🚗',
  MARGIN_LOANS: '📈',
  OVERDRAFTS: '💸',
  BUSINESS_LOANS: '🏢',
  TRADE_FINANCE: '🌏',
};

const WEIGHT_PROFILES: { value: WeightProfile; label: string; description: string }[] = [
  { value: 'balanced', label: 'Balanced', description: 'Equal weighting across all factors' },
  { value: 'fee_conscious', label: 'Fee Conscious', description: 'Minimise fees and charges' },
  { value: 'rate_focused', label: 'Rate Focused', description: 'Prioritise best interest rates' },
  { value: 'feature_rich', label: 'Feature Rich', description: 'Maximise product features' },
];

const AVAILABLE_FEATURES = [
  'OFFSET', 'REDRAW', 'DIGITAL_BANKING', 'NPP_PAYID', 'OVERDRAFT_PROTECTION',
  'CREDIT_CARD', 'LOYALTY_PROGRAM', 'FREE_TXNS', 'INTEREST_FREE',
];

type Step = 'category' | 'profile' | 'preferences' | 'weight' | 'review' | 'running' | 'done';

export function DiscoveryWizard() {
  const navigate = useNavigate();
  const [step, setStep] = useState<Step>('category');
  const [selectedCategory, setSelectedCategory] = useState<ProductCategory | null>(null);
  const [userIntent, setUserIntent] = useState('');
  const [preferences, setPreferences] = useState<ClientPreferences>({});
  const [selectedFeatures, setSelectedFeatures] = useState<string[]>([]);
  const [weightProfile, setWeightProfile] = useState<WeightProfile>('balanced');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (!selectedCategory || !userIntent) return;
    setSubmitting(true);
    setStep('running');
    setError(null);
    try {
      const session = await createSession({
        userIntent,
        productCategory: selectedCategory,
        preferences: { ...preferences, requiredFeatures: selectedFeatures },
        constraints: {},
        weightProfile,
      });
      setSessionId(session.id);
      const completed = await pollSession(session.id);
      if (completed.status === 'completed') {
        setStep('done');
      } else {
        setError(completed.errorMessage || 'Discovery failed');
        setStep('review');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start discovery');
      setStep('review');
    } finally {
      setSubmitting(false);
    }
  };

  if (step === 'running') {
    return (
      <div data-testid="discovery-wizard">
        <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.5rem' }}>Product Discovery</h2>
        <LoadingSpinner message="Running discovery analysis... This may take up to 2 minutes." />
      </div>
    );
  }

  if (step === 'done' && sessionId) {
    return (
      <div data-testid="discovery-wizard" style={{ textAlign: 'center', padding: '4rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.5rem' }}>Product Discovery</h2>
        <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>✅</div>
        <h3>Discovery Complete!</h3>
        <p style={{ color: 'var(--color-gray-600)', margin: '1rem 0' }}>
          Your product discovery report is ready.
        </p>
        <button className="btn-primary" onClick={() => navigate(`/reports/${sessionId}`)}>
          View Report
        </button>
      </div>
    );
  }

  return (
    <div data-testid="discovery-wizard">
      <div style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--color-gray-900)' }}>
          Product Discovery
        </h2>
        <p style={{ color: 'var(--color-gray-600)', marginTop: '0.25rem' }}>
          Find the best Australian financial products for your needs
        </p>
      </div>

      {/* Step indicator */}
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '2rem' }}>
        {(['category', 'profile', 'preferences', 'weight', 'review'] as Step[]).map((s, i) => (
          <div key={s} style={{
            flex: 1,
            height: 4,
            borderRadius: 2,
            background: s === step || (['category', 'profile', 'preferences', 'weight', 'review'] as Step[]).indexOf(step) > i
              ? 'var(--color-primary)' : 'var(--color-gray-200)',
          }} />
        ))}
      </div>

      {error && (
        <div className="card" style={{ background: '#fee2e2', border: '1px solid #fca5a5', marginBottom: '1rem' }}>
          <p style={{ color: '#991b1b', fontSize: '0.875rem' }}>⚠️ {error}</p>
        </div>
      )}

      {/* Step 1: Category */}
      {step === 'category' && (
        <div className="card">
          <h3 style={{ marginBottom: '1.5rem', fontSize: '1.1rem' }}>Select Product Category</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: '1rem' }}>
            {(Object.keys(PRODUCT_CATEGORY_LABELS) as ProductCategory[]).map(cat => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: '0.5rem',
                  padding: '1.25rem',
                  border: `2px solid ${selectedCategory === cat ? 'var(--color-primary)' : 'var(--color-gray-200)'}`,
                  borderRadius: 'var(--radius)',
                  background: selectedCategory === cat ? '#eff6ff' : 'white',
                  cursor: 'pointer',
                  transition: 'all 0.15s',
                }}
              >
                <span style={{ fontSize: '2rem' }}>{CATEGORY_ICONS[cat]}</span>
                <span style={{ fontSize: '0.8rem', fontWeight: 500, textAlign: 'center' }}>
                  {PRODUCT_CATEGORY_LABELS[cat]}
                </span>
              </button>
            ))}
          </div>
          <div style={{ marginTop: '1.5rem', display: 'flex', justifyContent: 'flex-end' }}>
            <button
              className="btn-primary"
              disabled={!selectedCategory}
              onClick={() => setStep('profile')}
              style={{ opacity: selectedCategory ? 1 : 0.5 }}
            >
              Next →
            </button>
          </div>
        </div>
      )}

      {/* Step 2: Profile */}
      {step === 'profile' && (
        <div className="card">
          <h3 style={{ marginBottom: '1.5rem', fontSize: '1.1rem' }}>What are you looking for?</h3>
          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', fontWeight: 500, marginBottom: '0.5rem', fontSize: '0.875rem' }}>
              Describe your goal *
            </label>
            <input
              type="text"
              value={userIntent}
              onChange={e => setUserIntent(e.target.value)}
              placeholder="e.g. I want a savings account with high interest and no monthly fees"
              style={{
                width: '100%',
                padding: '0.75rem',
                border: '1px solid var(--color-gray-200)',
                borderRadius: 'var(--radius)',
                fontSize: '0.875rem',
              }}
            />
          </div>
          <div style={{ marginTop: '1.5rem', display: 'flex', justifyContent: 'space-between' }}>
            <button className="btn-secondary" onClick={() => setStep('category')}>← Back</button>
            <button
              className="btn-primary"
              disabled={!userIntent.trim()}
              onClick={() => setStep('preferences')}
              style={{ opacity: userIntent.trim() ? 1 : 0.5 }}
            >
              Next →
            </button>
          </div>
        </div>
      )}

      {/* Step 3: Preferences */}
      {step === 'preferences' && (
        <div className="card">
          <h3 style={{ marginBottom: '1.5rem', fontSize: '1.1rem' }}>Preferences & Constraints</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
            <div>
              <label style={{ display: 'block', fontWeight: 500, marginBottom: '0.5rem', fontSize: '0.875rem' }}>
                Max Monthly Fee (AUD)
              </label>
              <input
                type="number"
                value={preferences.maxMonthlyFee ?? ''}
                onChange={e => setPreferences(p => ({ ...p, maxMonthlyFee: e.target.value ? Number(e.target.value) : undefined }))}
                placeholder="e.g. 10"
                style={{ width: '100%', padding: '0.75rem', border: '1px solid var(--color-gray-200)', borderRadius: 'var(--radius)', fontSize: '0.875rem' }}
              />
            </div>
            <div>
              <label style={{ display: 'block', fontWeight: 500, marginBottom: '0.5rem', fontSize: '0.875rem' }}>
                Target Rate (%)
              </label>
              <input
                type="number"
                step="0.01"
                value={preferences.targetRate != null ? preferences.targetRate * 100 : ''}
                onChange={e => setPreferences(p => ({ ...p, targetRate: e.target.value ? Number(e.target.value) / 100 : undefined }))}
                placeholder="e.g. 5.5"
                style={{ width: '100%', padding: '0.75rem', border: '1px solid var(--color-gray-200)', borderRadius: 'var(--radius)', fontSize: '0.875rem' }}
              />
            </div>
          </div>
          <div>
            <label style={{ display: 'block', fontWeight: 500, marginBottom: '0.75rem', fontSize: '0.875rem' }}>
              Required Features
            </label>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
              {AVAILABLE_FEATURES.map(f => (
                <label key={f} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', cursor: 'pointer', padding: '0.4rem 0.75rem', border: `1px solid ${selectedFeatures.includes(f) ? 'var(--color-primary)' : 'var(--color-gray-200)'}`, borderRadius: 'var(--radius)', background: selectedFeatures.includes(f) ? '#eff6ff' : 'white', fontSize: '0.8rem' }}>
                  <input
                    type="checkbox"
                    checked={selectedFeatures.includes(f)}
                    onChange={e => setSelectedFeatures(prev => e.target.checked ? [...prev, f] : prev.filter(x => x !== f))}
                  />
                  {f.replace(/_/g, ' ')}
                </label>
              ))}
            </div>
          </div>
          <div style={{ marginTop: '1.5rem', display: 'flex', justifyContent: 'space-between' }}>
            <button className="btn-secondary" onClick={() => setStep('profile')}>← Back</button>
            <button className="btn-primary" onClick={() => setStep('weight')}>Next →</button>
          </div>
        </div>
      )}

      {/* Step 4: Weight Profile */}
      {step === 'weight' && (
        <div className="card">
          <h3 style={{ marginBottom: '1.5rem', fontSize: '1.1rem' }}>Scoring Weight Profile</h3>
          <p style={{ color: 'var(--color-gray-600)', fontSize: '0.875rem', marginBottom: '1.5rem' }}>
            Choose how to weight different factors when scoring and ranking products.
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            {WEIGHT_PROFILES.map(wp => (
              <button
                key={wp.value}
                onClick={() => setWeightProfile(wp.value)}
                style={{
                  padding: '1.25rem',
                  border: `2px solid ${weightProfile === wp.value ? 'var(--color-primary)' : 'var(--color-gray-200)'}`,
                  borderRadius: 'var(--radius)',
                  background: weightProfile === wp.value ? '#eff6ff' : 'white',
                  cursor: 'pointer',
                  textAlign: 'left',
                  transition: 'all 0.15s',
                }}
              >
                <p style={{ fontWeight: 600, marginBottom: '0.25rem', fontSize: '0.875rem' }}>{wp.label}</p>
                <p style={{ fontSize: '0.8rem', color: 'var(--color-gray-600)' }}>{wp.description}</p>
              </button>
            ))}
          </div>
          <div style={{ marginTop: '1.5rem', display: 'flex', justifyContent: 'space-between' }}>
            <button className="btn-secondary" onClick={() => setStep('preferences')}>← Back</button>
            <button className="btn-primary" onClick={() => setStep('review')}>Next →</button>
          </div>
        </div>
      )}

      {/* Step 5: Review */}
      {step === 'review' && (
        <div className="card">
          <h3 style={{ marginBottom: '1.5rem', fontSize: '1.1rem' }}>Review & Submit</h3>
          <div style={{ background: 'var(--color-gray-50)', borderRadius: 'var(--radius)', padding: '1rem', marginBottom: '1.5rem' }}>
            <dl style={{ display: 'grid', gridTemplateColumns: 'auto 1fr', gap: '0.5rem 1rem' }}>
              <dt style={{ fontWeight: 500, fontSize: '0.875rem', color: 'var(--color-gray-600)' }}>Category:</dt>
              <dd style={{ fontSize: '0.875rem' }}>{selectedCategory ? PRODUCT_CATEGORY_LABELS[selectedCategory] : '-'}</dd>
              <dt style={{ fontWeight: 500, fontSize: '0.875rem', color: 'var(--color-gray-600)' }}>Intent:</dt>
              <dd style={{ fontSize: '0.875rem' }}>{userIntent}</dd>
              <dt style={{ fontWeight: 500, fontSize: '0.875rem', color: 'var(--color-gray-600)' }}>Weight:</dt>
              <dd style={{ fontSize: '0.875rem' }}>{WEIGHT_PROFILES.find(w => w.value === weightProfile)?.label}</dd>
              {selectedFeatures.length > 0 && (
                <>
                  <dt style={{ fontWeight: 500, fontSize: '0.875rem', color: 'var(--color-gray-600)' }}>Features:</dt>
                  <dd style={{ fontSize: '0.875rem' }}>{selectedFeatures.join(', ')}</dd>
                </>
              )}
            </dl>
          </div>
          <div className="card" style={{ background: '#fef3c7', border: '1px solid #fcd34d', marginBottom: '1.5rem' }}>
            <p style={{ fontSize: '0.8rem', color: '#92400e' }}>
              ⚠️ <strong>Disclaimer:</strong> Results are for product discovery purposes only and do not constitute personal financial advice.
            </p>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <button className="btn-secondary" onClick={() => setStep('weight')}>← Back</button>
            <button
              className="btn-primary"
              disabled={submitting}
              onClick={handleSubmit}
            >
              {submitting ? 'Starting...' : '🔍 Start Discovery'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
