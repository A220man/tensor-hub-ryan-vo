import type { IssueResponse, AnalysisResponse, TestCaseResponse } from '../types/api';
import { useState } from 'react';

interface IssueDetailProps {
  issue: IssueResponse;
  analysis?: AnalysisResponse;
  testCase?: TestCaseResponse;
  onClose: () => void;
  onReanalyze: () => void;
  onAnalyzeNew: (title: string, body: string) => void;
}

const h5Style = {
  fontSize: '0.8rem',
  fontWeight: 600,
  marginBottom: '0.25rem',
  color: 'var(--color-text-muted)',
};

export function IssueDetail({ issue, analysis, testCase, onClose, onReanalyze, onAnalyzeNew }: IssueDetailProps) {
  const [showAnalyzeForm, setShowAnalyzeForm] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newBody, setNewBody] = useState('');

  const handleAnalyzeNew = (e: React.FormEvent) => {
    e.preventDefault();
    if (newTitle.trim() && newBody.trim()) {
      onAnalyzeNew(newTitle, newBody);
      setShowAnalyzeForm(false);
      setNewTitle('');
      setNewBody('');
    }
  };

  return (
    <div style={{ position: 'fixed', top: 0, right: 0, bottom: 0, width: '70vw', maxWidth: '900px', background: 'var(--color-bg-secondary)', borderLeft: '1px solid var(--color-border)', boxShadow: '-4px 0 20px rgba(0,0,0,0.3)', zIndex: 100, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      <header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '1rem 1.5rem', borderBottom: '1px solid var(--color-border)', background: 'var(--color-bg-tertiary)', flexShrink: 0 }}>
        <h2 style={{ fontSize: '1.1rem', fontWeight: 600 }}>{issue.title}</h2>
        <button
          onClick={onClose}
          style={{ background: 'transparent', color: 'var(--color-text-muted)', padding: '0.5rem', borderRadius: 'var(--radius)', fontSize: '1.2rem', lineHeight: 1 }}
          aria-label="Close"
        >
          ×
        </button>
      </header>

      <div style={{ flex: 1, overflow: 'auto', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
          <span style={{ fontSize: '0.7rem', fontWeight: 600, textTransform: 'uppercase', padding: '0.25rem 0.5rem', borderRadius: '999px', background: 'var(--color-accent)20', color: 'var(--color-accent)' }}>
            {issue.category.replace('_', ' ')}
          </span>
          <span style={{ fontSize: '0.7rem', fontWeight: 600, textTransform: 'uppercase', padding: '0.25rem 0.5rem', borderRadius: '999px', background: 'var(--color-warning)20', color: 'var(--color-warning)' }}>
            {issue.status.replace('_', ' ')}
          </span>
          {issue.php_version && <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>PHP {issue.php_version}</span>}
          {issue.os && <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>{issue.os}</span>}
          {issue.github_number && (
            <a href={issue.html_url || '#'} target="_blank" rel="noopener noreferrer" style={{ fontSize: '0.75rem', color: 'var(--color-accent)' }}>
              GitHub #{issue.github_number}
            </a>
          )}
        </div>

        <div style={{ border: '1px solid var(--color-border)', borderRadius: 'var(--radius)', background: 'var(--color-bg)', padding: '1rem' }}>
          <h4 style={{ fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.5rem', color: 'var(--color-text-muted)' }}>Issue Description</h4>
          <div style={{ whiteSpace: 'pre-wrap', fontSize: '0.875rem', lineHeight: 1.6, maxHeight: '300px', overflow: 'auto' }}>
            {issue.body}
          </div>
        </div>

        {analysis && (
          <div style={{ border: '1px solid var(--color-border)', borderRadius: 'var(--radius)', background: 'var(--color-bg)', padding: '1rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <h4 style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--color-text-muted)' }}>Analysis</h4>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap', fontSize: '0.875rem' }}>
              <span style={{ color: 'var(--color-accent)' }}>Classification: <strong>{analysis.classification}</strong></span>
              <span style={{ color: 'var(--color-success)' }}>Confidence: <strong>{analysis.confidence}%</strong></span>
            </div>
            {analysis.stack_trace && (
              <div>
                <h5 style={h5Style}>Stack Trace</h5>
                <pre style={{ fontSize: '0.75rem', maxHeight: '200px', overflow: 'auto' }}>{analysis.stack_trace}</pre>
              </div>
            )}
            {analysis.error_patterns && analysis.error_patterns.length > 0 && (
              <div>
                <h5 style={h5Style}>Error Patterns</h5>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem' }}>
                  {analysis.error_patterns.map((p: string, i: number) => (
                    <span key={i} style={{ fontSize: '0.7rem', padding: '0.125rem 0.375rem', background: 'var(--color-code-bg)', border: '1px solid var(--color-border)', borderRadius: '999px', fontFamily: 'var(--font-mono)' }}>{p}</span>
                  ))}
                </div>
              </div>
            )}
            {analysis.root_cause && (
              <div>
                <h5 style={h5Style}>Root Cause</h5>
                <p style={{ fontSize: '0.875rem', lineHeight: 1.6 }}>{analysis.root_cause}</p>
              </div>
            )}
            {analysis.suggested_fix && (
              <div>
                <h5 style={h5Style}>Suggested Fix</h5>
                <p style={{ fontSize: '0.875rem', lineHeight: 1.6 }}>{analysis.suggested_fix}</p>
              </div>
            )}
          </div>
        )}

        {testCase && (
          <div style={{ border: '1px solid var(--color-border)', borderRadius: 'var(--radius)', background: 'var(--color-bg)', padding: '1rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <h4 style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--color-text-muted)' }}>Generated Test Case</h4>
              <span style={{ fontSize: '0.7rem', padding: '0.125rem 0.375rem', background: 'var(--color-success)20', color: 'var(--color-success)', borderRadius: '999px' }}>{testCase.status}</span>
            </div>
            {testCase.description && <p style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>{testCase.description}</p>}
            <pre style={{ fontSize: '0.75rem', maxHeight: '300px', overflow: 'auto' }}>{testCase.code}</pre>
            {testCase.expected_behavior && (
              <div style={{ padding: '0.5rem', background: 'var(--color-success)10', border: '1px solid var(--color-success)30', borderRadius: 'var(--radius)', fontSize: '0.8rem' }}>
                <strong style={{ color: 'var(--color-success)' }}>Expected: </strong>{testCase.expected_behavior}
              </div>
            )}
          </div>
        )}

        {!analysis && (
          <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--color-text-muted)' }}>
            <p>No analysis available yet.</p>
            <button onClick={onReanalyze} style={{ marginTop: '1rem', padding: '0.5rem 1rem', background: 'var(--color-accent)', color: 'var(--color-bg)' }}>
              Run Analysis
            </button>
          </div>
        )}

        {showAnalyzeForm && (
          <form onSubmit={handleAnalyzeNew} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', borderTop: '1px solid var(--color-border)', paddingTop: '1.5rem' }}>
            <h4 style={{ fontSize: '0.85rem', fontWeight: 600 }}>Analyze New Issue</h4>
            <input
              type="text"
              placeholder="Issue title"
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              required
            />
            <textarea
              placeholder="Issue description..."
              value={newBody}
              onChange={(e) => setNewBody(e.target.value)}
              rows={6}
              required
            />
            <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end' }}>
              <button type="button" onClick={() => setShowAnalyzeForm(false)} style={{ background: 'var(--color-bg-tertiary)', color: 'var(--color-text)' }}>
                Cancel
              </button>
              <button type="submit" style={{ background: 'var(--color-accent)', color: 'var(--color-bg)' }}>
                Analyze
              </button>
            </div>
          </form>
        )}

        {!showAnalyzeForm && (
          <button onClick={() => setShowAnalyzeForm(true)} style={{ alignSelf: 'flex-start', padding: '0.5rem 1rem', background: 'var(--color-bg-tertiary)', color: 'var(--color-text)', border: '1px solid var(--color-border)' }}>
            + Analyze Another Issue
          </button>
        )}
      </div>
    </div>
  );
}