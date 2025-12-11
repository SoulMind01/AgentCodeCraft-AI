import React from 'react';
import { Link } from 'react-router-dom';

const NotFoundPage: React.FC = () => (
  <div className="page center">
    <h1>404 - Not Found</h1>
    <p className="small-muted">
      The page you are looking for does not exist.
    </p>
    <Link to="/runs" className="link">
      Go to dashboard
    </Link>
  </div>
);

export default NotFoundPage;