import React from 'react';
import { Link } from 'react-router-dom';
import { useRuns } from '../api/hooks';
import Loader from '../components/shared/Loader';
import ErrorState from '../components/shared/ErrorState';
import RunTable from '../components/runs/RunTable';

const DashboardPage: React.FC = () => {
  const { data: runs, isLoading, isError } = useRuns();

  return (
    <div className="page">
      <div className="page-header">
        <h1>Runs</h1>
        <Link to="/new" className="button-primary">
          New Run
        </Link>
      </div>

      {isLoading && <Loader />}
      {isError && <ErrorState message="Failed to load runs." />}
      {runs && <RunTable runs={runs} />}
    </div>
  );
};

export default DashboardPage;