import React from 'react';

interface ErrorStateProps {
  message?: string;
}

const ErrorState: React.FC<ErrorStateProps> = ({
  message = 'Something went wrong.',
}) => (
  <div className="state-message state-message-error">{message}</div>
);

export default ErrorState;