import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { usePolicies, useStartRefactor } from '../api/hooks';
import Loader from '../components/shared/Loader';
import ErrorState from '../components/shared/ErrorState';
import type { StartRefactorPayload } from '../api/types';

const NewRunPage: React.FC = () => {
  const { data: policies, isLoading, isError } = usePolicies();
  const startRefactor = useStartRefactor();
  const navigate = useNavigate();

  const [language, setLanguage] = useState<'python' | 'terraform'>('python');
  const [mode, setMode] = useState<'auto' | 'suggest'>('suggest');
  const [runTests, setRunTests] = useState(true);
  const [selectedPolicyIds, setSelectedPolicyIds] = useState<string[]>([]);
  const [files, setFiles] = useState<{ path: string; content: string }[]>([]);

  const handleStart = async () => {
    if (!files.length || !selectedPolicyIds.length) return;
    const payload: StartRefactorPayload = {
      language,
      mode,
      run_tests: runTests,
      files,
      policy_ids: selectedPolicyIds,
    };
    const result = await startRefactor.mutateAsync(payload);
    navigate(`/runs/${result.run_id}`);
  };

  return (
    <div className="page page-narrow">
      <h1>New Run</h1>

      <section className="section">
        <h2>Language</h2>
        <div className="button-group">
          <button
            type="button"
            className={
              language === 'python' ? 'button-toggle active' : 'button-toggle'
            }
            onClick={() => setLanguage('python')}
          >
            Python
          </button>
          <button
            type="button"
            className={
              language === 'terraform'
                ? 'button-toggle active'
                : 'button-toggle'
            }
            onClick={() => setLanguage('terraform')}
          >
            Terraform
          </button>
        </div>
      </section>

      <section className="section">
        <h2>Mode</h2>
        <select
          value={mode}
          onChange={(e) => setMode(e.target.value as 'auto' | 'suggest')}
        >
          <option value="suggest">Suggest only (do not apply)</option>
          <option value="auto">Auto apply (experimental)</option>
        </select>
      </section>

      <section className="section">
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={runTests}
            onChange={(e) => setRunTests(e.target.checked)}
          />
          Run tests / validation
        </label>
      </section>

      <section className="section">
        <h2>Policies</h2>
        {isLoading && <Loader message="Loading policies..." />}
        {isError && <ErrorState message="Failed to load policies." />}
        {policies && (
          <div className="box scroll">
            {policies.map((p) => {
              const selected = selectedPolicyIds.includes(p.policy_id);
              return (
                <label key={p.policy_id} className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={selected}
                    onChange={(e) => {
                      setSelectedPolicyIds((prev) =>
                        e.target.checked
                          ? [...prev, p.policy_id]
                          : prev.filter((id) => id !== p.policy_id)
                      );
                    }}
                  />
                  <span>{p.name}</span>
                  <span className="small-muted">
                    {p.language} v{p.version}
                  </span>
                </label>
              );
            })}
          </div>
        )}
      </section>

      <section className="section">
        <h2>Files</h2>
        <p className="small-muted">
          TODO: Replace with drag-and-drop uploader. For now, use a stub file.
        </p>
        <button
          type="button"
          className="link-button"
          onClick={() =>
            setFiles([
              {
                path: 'example.py',
                content: 'print("hello from stub")',
              },
            ])
          }
        >
          Add example stub file
        </button>
        <ul className="small-muted">
          {files.map((f) => (
            <li key={f.path}>
              {f.path} ({f.content.length} chars)
            </li>
          ))}
        </ul>
      </section>

      <button
        type="button"
        className="button-primary"
        disabled={
          startRefactor.isPending ||
          !files.length ||
          !selectedPolicyIds.length
        }
        onClick={handleStart}
      >
        {startRefactor.isPending ? 'Starting…' : 'Start Refactor'}
      </button>
    </div>
  );
};

export default NewRunPage;