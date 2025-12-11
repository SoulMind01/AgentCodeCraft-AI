import React from 'react';

const Topbar: React.FC = () => {
  return (
    <header className="topbar">
      <div className="topbar-left">Policy-driven refactoring dashboard</div>
      <div className="topbar-right">
        <span className="topbar-user-label">Signed in as</span>
        <span className="topbar-user-name">demo@user</span>
      </div>
    </header>
  );
};

export default Topbar;