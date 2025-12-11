import React from 'react';
import { usePolicies } from '../api/hooks';
import Loader from '../components/shared/Loader';
import ErrorState from '../components/shared/ErrorState';

const PoliciesPage: React.FC = () => {
  const { data: policies, isLoading, isError } = usePolicies();

  return (
    <div className="page page-narrow">
      <h1>Policies</h1>

      {isLoading && <Loader message="Loading policies..." />}
      {isError && <ErrorState message="Failed to load policies." />}
      {policies && (
        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Language</th>
                <th>Version</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {policies.map((p) => (
                <tr key={p.policy_id}>
                  <td>{p.name}</td>
                  <td>{p.language}</td>
                  <td>{p.version}</td>
                  <td className="small-muted">
                    {new Date(p.created_at).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <p className="small-muted">
        TODO: Add YAML editor and /api/policies/validate integration.
      </p>
    </div>
  );
};

export default PoliciesPage;