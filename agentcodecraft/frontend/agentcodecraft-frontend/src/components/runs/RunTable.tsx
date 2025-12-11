import React from 'react';
import { Link } from 'react-router-dom';
import type { RunSummary } from '../../api/types';

interface Props {
  runs: RunSummary[];
}

const RunTable: React.FC<Props> = ({ runs }) => {
  if (!runs.length) {
    return <div className="small-muted">No runs yet.</div>;
  }

  return (
    <div className="table-container">
      <table className="table">
        <thead>
          <tr>
            <th>Run ID</th>
            <th>Status</th>
            <th>Language</th>
            <th>Score</th>
            <th>Started</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {runs.map((run) => (
            <tr key={run.run_id}>
              <td className="mono">{run.run_id}</td>
              <td>
                <span className={`status-pill status-${run.status}`}>
                  {run.status}
                </span>
              </td>
              <td>{run.language}</td>
              <td>
                {run.compliance_score != null
                  ? `${Math.round(run.compliance_score * 100)}%`
                  : '—'}
              </td>
              <td className="small-muted">
                {new Date(run.started_at).toLocaleString()}
              </td>
              <td>
                <Link to={`/runs/${run.run_id}`} className="link">
                  View
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default RunTable;