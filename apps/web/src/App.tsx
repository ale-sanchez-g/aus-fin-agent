import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppShell } from './components/layout/AppShell';
import { Dashboard } from './pages/Dashboard';
import { DiscoveryWizard } from './pages/DiscoveryWizard';
import { ProductComparison } from './pages/ProductComparison';
import { ReportViewer } from './pages/ReportViewer';
import { SyncStatus } from './pages/SyncStatus';
import { NotFound } from './pages/NotFound';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AppShell />}>
          <Route index element={<Dashboard />} />
          <Route path="discover" element={<DiscoveryWizard />} />
          <Route path="products" element={<ProductComparison />} />
          <Route path="reports/:sessionId" element={<ReportViewer />} />
          <Route path="sync-status" element={<SyncStatus />} />
          <Route path="404" element={<NotFound />} />
          <Route path="*" element={<Navigate to="/404" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
