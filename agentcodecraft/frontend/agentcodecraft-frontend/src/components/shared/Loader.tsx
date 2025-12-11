import React from 'react';

interface LoaderProps {
  message?: string;
}

const Loader: React.FC<LoaderProps> = ({ message = 'Loading...' }) => (
  <div className="state-message">{message}</div>
);

export default Loader;