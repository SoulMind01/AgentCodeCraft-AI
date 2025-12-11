import React from 'react';
import AppLayout from './components/layout/AppLayout';
import AppRouter from './router/AppRouter';

const App: React.FC = () => {
  return (
    <AppLayout>
      <AppRouter />
    </AppLayout>
  );
};

export default App;