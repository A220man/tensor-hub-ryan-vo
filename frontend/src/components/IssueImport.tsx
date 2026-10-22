import { useState } from 'react';
import { useCreateIssue, useAnalyzeIssue } from '../hooks/useIssues';
import type { IssueCreate, AnalyzeRequest } from '../types/api';

const labelStyle = {
  display: 'block',
  fontSize: '0.75rem',
  fontWeight: 500,
  marginBottom: '0.25rem',
};

export function IssueImport({ onClose, onSuccess }: { onClose: () => void; onSuccess: () => void }) {
  const [mode, setMode] = useState<'github' | 'manual'>('github');
  const [githubUrl, setGithubUrl] = useState('');
  const [title, setTitle] = useState('');
  const [body, setBody] = useState('');
  const [phpVersion, setPhpVersion] = useState('');
  const [os, setOs] = useState('');

  const createMutation = useCreateIssue();
  const analyzeMutation = useAnalyzeIssue();

  const isLoading = createMutation.isPending || analyzeMutation.isPending;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    let issueData: IssueCreate;

    if (mode === 'github' && githubUrl.trim()) {
      const match = githubUrl.match(/github\.com\/[^/]+\/[^/]+\/issues\/(\d+)/);
      const githubNumber = match ? parseInt(match[1], 10) : undefined;

      issueData = {
        github_number: githubNumber,
        title: title.trim() || 'Imported from GitHub',
        body: body.trim() || githubUrl.trim(),
        html_url: githubUrl.trim(),
        php_version: phpVersion.trim() || undefined,
        os: os.trim() || undefined,
        comments_count: 0,
      };
    } else {
      issueData = {
        title: title.trim(),
        body: body.trim(),
        php_version: phpVersion.trim() || undefined,
        os: os.trim() || undefined,
        comments_count: 0,
      };
    }

    if (!issueData.title || !issueData.body) {
      alert('Title and body are required');
      return;
    }

    try {
      await createMutation.mutateAsync(issueData);
      onSuccess();
      onClose();
    } catch (error) {
      console.error('Failed to create issue:', error);
      alert('Failed to import issue. Check console for details.');
    }
  };

  const handleAnalyzeOnly = async (e: React.FormEvent) => {
    e.preventDefault();

    const analyzeData: AnalyzeRequest = {
      title: title.trim(),
      body: body.trim(),
      php_version: phpVersion.trim() || undefined,
      os: os.trim() || undefined,
    };

    if (!analyzeData.title || !analyzeData.body) {
      alert('Title and body are required');
      return;
    }

    try {
      const result = await analyzeMutation.mutateAsync(analyzeData);
      alert(`Analysis complete: ${result.analysis.classification} (${result.analysis.confidence}% confidence)`);
      onClose();
    } catch (error) {
      console.error('Analysis failed:', error);
      alert('Analysis failed. Check console for details.');
    }
  };

  return (
    <div style={{ position: 'fixed', top: 0, right: 0, bottom: 0, width: '50vw', maxWidth: '600px', background: 'var(--color-bg-secondary)', borderLeft: '1px solid var(--color-border)', boxShadow: '-4px 0 20px rgba(0,0,0,0.3)', zIndex: 100, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      <header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '1rem 1.5rem', borderBottom: '1px solid var(--color-border)', background: 'var(--color-bg-tertiary)', flexShrink: 0 }}>
        <h2 style={{ fontSize: '1.1rem', fontWeight: 600 }}>Import Issue</h2>
        <button
          onClick={onClose}
          disabled={isLoading}
          style={{ background: 'transparent', color: 'var(--color-text-muted)', padding: '0.5rem', borderRadius: 'var(--radius)', fontSize: '1.2rem', lineHeight: 1 }}
          aria-label="Close"
        >
          ×
        </button>
      </header>

      <form onSubmit={mode === 'github' ? handleSubmit : handleAnalyzeOnly} style={{ flex: 1, overflow: 'auto', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button
            type="button"
            onClick={() => setMode('github')}
            style={{
              flex: 1,
              padding: '0.5rem',
              borderRadius: 'var(--radius)',
              background: mode === 'github' ? 'var(--color-accent)' : 'var(--color-bg-tertiary)',
              color: mode === 'github' ? 'var(--color-bg)' : 'var(--color-text)',
              border: '1px solid var(--color-border)',
            }}
          >
            From GitHub URL
          </button>
          <button
            type="button"
            onClick={() => setMode('manual')}
            style={{
              flex: 1,
              padding: '0.5rem',
              borderRadius: 'var(--radius)',
              background: mode === 'manual' ? 'var(--color-accent)' : 'var(--color-bg-tertiary)',
              color: mode === 'manual' ? 'var(--color-bg)' : 'var(--color-text)',
              border: '1px solid var(--color-border)',
            }}
          >
            Manual Entry
          </button>
        </div>

        {mode === 'github' && (
          <div>
            <label style={labelStyle}>
              GitHub Issue URL
            </label>
            <input
              type="url"
              placeholder="https://github.com/php/php-src/issues/12345"
              value={githubUrl}
              onChange={(e) => setGithubUrl(e.target.value)}
              required
            />
            <p style={{ fontSize: '0.7rem', color: 'var(--color-text-muted)', marginTop: '0.25rem' }}>
              Title and body will be fetched from the issue. You can override them below.
            </p>
          </div>
        )}

        <div>
          <label style={labelStyle}>
            Title *
          </label>
          <input
            type="text"
            placeholder="Issue title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
        </div>

        <div>
          <label style={labelStyle}>
            Description / Body *
          </label>
          <textarea
            placeholder="Paste issue description, stack trace, error messages..."
            value={body}
            onChange={(e) => setBody(e.target.value)}
            rows={8}
            required
          />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
          <div>
            <label style={labelStyle}>
              PHP Version
            </label>
            <input
              type="text"
              placeholder="8.1.1"
              value={phpVersion}
              onChange={(e) => setPhpVersion(e.target.value)}
            />
          </div>
          <div>
            <label style={labelStyle}>
              Operating System
            </label>
            <input
              type="text"
              placeholder="Ubuntu 22.04, macOS 13.5, etc."
              value={os}
              onChange={(e) => setOs(e.target.value)}
            />
          </div>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end', marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--color-border)' }}>
          <button type="button" onClick={onClose} disabled={isLoading} style={{ background: 'var(--color-bg-tertiary)', color: 'var(--color-text)', border: '1px solid var(--color-border)' }}>
            Cancel
          </button>
          <button type="submit" disabled={isLoading} style={{ background: 'var(--color-accent)', color: 'var(--color-bg)' }}>
            {isLoading ? 'Processing...' : mode === 'github' ? 'Import & Analyze' : 'Analyze Only'}
          </button>
        </div>
      </form>
    </div>
  );
}