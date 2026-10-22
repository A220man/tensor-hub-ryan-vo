import { useState } from 'react';
import { useIssues, useReanalyzeIssue } from '../hooks/useIssues';
import { IssueCard } from './IssueCard';
import { IssueDetail } from './IssueDetail';
import { IssueImport } from './IssueImport';
import type { IssueResponse } from '../types/api';

export function Dashboard() {
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [category, setCategory] = useState<string>('');
  const [status, setStatus] = useState<string>('');
  const [selectedIssue, setSelectedIssue] = useState<IssueResponse | null>(null);
  const [showImport, setShowImport] = useState(false);

  const { data, isLoading, error, refetch } = useIssues(page, pageSize, category || undefined, status || undefined);
  const reanalyzeMutation = useReanalyzeIssue();

  const handleReanalyze = async (id: number) => {
    try {
      await reanalyzeMutation.mutateAsync(id);
      refetch();
    } catch (err) {
      console.error('Reanalyze failed:', err);
    }
  };

  if (isLoading && !data) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '400px', color: 'var(--color-text-muted)' }}>
        Loading issues…
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '400px', color: 'var(--color-error)' }}>
        Error loading issues: {String(error)}
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
      <header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '1rem 1.5rem', borderBottom: '1px solid var(--color-border)', background: 'var(--color-bg-tertiary)', flexShrink: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <h1 style={{ fontSize: '1.25rem', fontWeight: 600 }}>PHP Issue Analyzer</h1>
          <span style={{ fontSize: '0.7rem', color: 'var(--color-text-muted)', padding: '0.125rem 0.5rem', background: 'var(--color-accent)20', borderRadius: '999px' }}>v1.0.0</span>
        </div>
        <button
          onClick={() => setShowImport(true)}
          style={{
            padding: '0.5rem 1rem',
            background: 'var(--color-accent)',
            color: 'var(--color-bg)',
            borderRadius: 'var(--radius)',
            fontWeight: 500,
          }}
        >
          + Import Issue
        </button>
      </header>

      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        <aside style={{ width: '360px', minWidth: '320px', maxWidth: '480px', borderRight: '1px solid var(--color-border)', background: 'var(--color-bg-secondary)', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <div style={{ padding: '1rem', borderBottom: '1px solid var(--color-border)', flexShrink: 0 }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <select
                  value={category}
                  onChange={(e) => { setCategory(e.target.value); setPage(1); }}
                  style={{ flex: 1, fontSize: '0.8rem' }}
                >
                  <option value="">All Categories</option>
                  <option value="segfault">Segfault</option>
                  <option value="performance">Performance</option>
                  <option value="memory">Memory</option>
                  <option value="logic_bug">Logic Bug</option>
                  <option value="platform_specific">Platform Specific</option>
                  <option value="feature_request">Feature Request</option>
                  <option value="unknown">Unknown</option>
                </select>
                <select
                  value={status}
                  onChange={(e) => { setStatus(e.target.value); setPage(1); }}
                  style={{ flex: 1, fontSize: '0.8rem' }}
                >
                  <option value="">All Statuses</option>
                  <option value="new">New</option>
                  <option value="analyzing">Analyzing</option>
                  <option value="analyzed">Analyzed</option>
                  <option value="test_generated">Test Generated</option>
                  <option value="closed">Closed</option>
                </select>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                <span>{data?.total || 0} issues</span>
                {data && data.total > pageSize && (
                  <>
                    <button
                      onClick={() => setPage(p => Math.max(1, p - 1))}
                      disabled={page <= 1}
                      style={{ padding: '0.25rem 0.5rem', background: 'var(--color-bg-tertiary)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius)', fontSize: '0.75rem' }}
                    >
                      Prev
                    </button>
                    <span>Page {page}</span>
                    <button
                      onClick={() => setPage(p => p + 1)}
                      disabled={page * pageSize >= (data?.total || 0)}
                      style={{ padding: '0.25rem 0.5rem', background: 'var(--color-bg-tertiary)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius)', fontSize: '0.75rem' }}
                    >
                      Next
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>

          <div style={{ flex: 1, overflow: 'auto', padding: '0.5rem' }}>
            {data?.items.length === 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '200px', color: 'var(--color-text-muted)', textAlign: 'center', padding: '1rem' }}>
                <p style={{ fontSize: '0.9rem' }}>No issues found</p>
                <p style={{ fontSize: '0.75rem', marginTop: '0.5rem' }}>Import a GitHub issue or enter one manually to get started.</p>
              </div>
            ) : (
              data?.items.map((issue: IssueResponse) => (
                <IssueCard
                  key={issue.id}
                  issue={issue}
                  onClick={() => setSelectedIssue(issue)}
                />
              ))
            )}
          </div>
        </aside>

        <main style={{ flex: 1, overflow: 'auto', position: 'relative' }}>
          {selectedIssue ? (
            <IssueDetail
              issue={selectedIssue}
              onClose={() => setSelectedIssue(null)}
              onReanalyze={() => handleReanalyze(selectedIssue.id)}
              onAnalyzeNew={() => {
                setSelectedIssue(null);
                setShowImport(true);
              }}
            />
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--color-text-muted)', textAlign: 'center', padding: '2rem' }}>
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🔍</div>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 500, marginBottom: '0.5rem' }}>Select an issue to analyze</h2>
              <p style={{ fontSize: '0.9rem', maxWidth: '400px' }}>Choose an issue from the sidebar or import a new one to see analysis results, root cause, and generated test cases.</p>
            </div>
          )}
        </main>
      </div>

      {showImport && (
        <IssueImport
          onClose={() => setShowImport(false)}
          onSuccess={() => { refetch(); setShowImport(false); }}
        />
      )}
    </div>
  );
}