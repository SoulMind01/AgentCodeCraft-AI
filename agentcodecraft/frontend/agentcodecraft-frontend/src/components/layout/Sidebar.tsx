import React from 'react';
import { NavLink } from 'react-router-dom';

const Sidebar: React.FC = () => {
  const linkClass = ({ isActive }: { isActive: boolean }) =>
    'sidebar-link' + (isActive ? ' sidebar-link-active' : '');

  return (
    <aside className="sidebar">
      <div className="sidebar-title">AgentCodeCraft</div>
      <nav className="sidebar-nav">
        <NavLink to="/runs" className={linkClass}>
          Runs
        </NavLink>
        <NavLink to="/new" className={linkClass}>
          New Run
        </NavLink>
        <NavLink to="/policies" className={linkClass}>
          Policies
        </NavLink>
      </nav>
    </aside>
  );
};

export default Sidebar;