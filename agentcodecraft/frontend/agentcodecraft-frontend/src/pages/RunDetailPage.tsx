import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useRun } from '../api/hooks';
import Loader from '../components/shared/Loader';
import ErrorState from '../components/shared/ErrorState';

const RunDetailPage: React.FC = () => {
  const { runId } = useParams<{ runId: string }>();
  const { data: run, isLoading, isError } = useRun(runId || '');

  if (!runId) return <ErrorState message="Missing run ID." />;

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Run {runId}</h1>
          {run && (
            <p className="small-muted">
              Model {run.model_version} • Language {run.language}
            </p>
          )}
        </div>
        <Link to="/runs" className="link">
          Back to runs
        </Link>
      </div>

      {isLoading && <Loader />}
      {isError && <ErrorState message="Failed to load run." />}

      {run && (
        <>
          <section className="section-grid">
            <div className="box">
              <h2>Status</h2>
              <p>{run.status}</p>
            </div>
            <div className="box">
              <h2>Compliance</h2>
              <p>
                {run.compliance_score != null
                  ? `${Math.round(run.compliance_score * 100)}%`
                  : '—'}
              </p>
            </div>
            <div className="box">
              <h2>Duration</h2>
              <p>
                {run.finished_at
                  ? `${Math.round(
                      (new Date(run.finished_at).getTime() -
                        new Date(run.started_at).getTime()) /
                        1000
                    )} s`
                  : 'In progress'}
              </p>
            </div>
          </section>

          <section className="section">
            <h2>Findings</h2>
            <p className="small-muted">
              TODO: Replace with richer findings component.
            </p>
            <ul className="small-list scroll">
              {run.findings.map((f) => (
                <li key={f.finding_id}>
                  [{f.severity}] {f.file_path}:{f.line} — rule {f.rule_id} (
                  {f.status})
                </li>
              ))}
            </ul>
          </section>

          <section className="section">
            <h2>Artifacts</h2>
            <ul className="small-list">
              {run.artifacts.map((a) => (
                <li key={a.artifact_id}>
                  <a href={a.uri} target="_blank" rel="noreferrer">
                    {a.type} ({a.checksum.slice(0, 8)}…)
                  </a>
                </li>
              ))}
            </ul>
          </section>
        </>
      )}
    </div>
  );
};

export default RunDetailPage;