import React from 'react';
import { Routes, Route } from 'react-router-dom';
import DashboardPage from '../pages/DashboardPage';
import NewRunPage from '../pages/NewRunPage';
import RunDetailPage from '../pages/RunDetailPage';
import PoliciesPage from '../pages/PoliciesPage';
import NotFoundPage from '../pages/NotFoundPage';

const AppRouter: React.FC = () => {
  return (
    <Routes>
      <Route path="/" element={<DashboardPage />} />
      <Route path="/runs" element={<DashboardPage />} />
      <Route path="/runs/:runId" element={<RunDetailPage />} />
      <Route path="/new" element={<NewRunPage />} />
      <Route path="/policies" element={<PoliciesPage />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
};

export default AppRouter;