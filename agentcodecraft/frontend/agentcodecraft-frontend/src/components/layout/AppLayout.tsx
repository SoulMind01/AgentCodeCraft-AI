import React from 'react';
import Sidebar from './Sidebar';
import Topbar from './Topbar';
import '../../index.css';

interface AppLayoutProps {
  children: React.ReactNode;
}

const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  return (
    <div className="app-root">
      <Sidebar />
      <div className="app-main">
        <Topbar />
        <main className="app-content">{children}</main>
      </div>
    </div>
  );
};

export default AppLayout;