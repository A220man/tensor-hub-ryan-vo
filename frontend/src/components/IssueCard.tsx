import type { IssueResponse, IssueCategory } from '../types/api';

const categoryColors: Record<IssueCategory, string> = {
  segfault: '#f85149',
  performance: '#d29922',
  memory: '#a371f7',
  logic_bug: '#ffa657',
  platform_specific: '#79b8ff',
  feature_request: '#3fb950',
  unknown: '#8b949e',
};

const categoryLabels: Record<IssueCategory, string> = {
  segfault: 'Segfault',
  performance: 'Performance',
  memory: 'Memory',
  logic_bug: 'Logic Bug',
  platform_specific: 'Platform',
  feature_request: 'Feature',
  unknown: 'Unknown',
};

interface IssueCardProps {
  issue: IssueResponse;
  onClick: () => void;
}

export function IssueCard({ issue, onClick }: IssueCardProps) {
  const color = categoryColors[issue.category] || categoryColors.unknown;
  const label = categoryLabels[issue.category] || 'Unknown';

  return (
    <article
      className="issue-card"
      onClick={onClick}
      style={{
        background: 'var(--color-bg-secondary)',
        border: '1px solid var(--color-border)',
        borderRadius: 'var(--radius)',
        padding: '1rem',
        cursor: 'pointer',
        transition: 'border-color 150ms ease, box-shadow 150ms ease',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.75rem',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.borderColor = 'var(--color-accent)';
        e.currentTarget.style.boxShadow = '0 0 0 1px var(--color-accent)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.borderColor = 'var(--color-border)';
        e.currentTarget.style.boxShadow = 'none';
      }}
    >
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '1rem' }}>
        <h3 style={{ fontSize: '1rem', fontWeight: 600, lineHeight: 1.4, flex: 1 }}>
          {issue.title}
        </h3>
        <span
          style={{
            fontSize: '0.7rem',
            fontWeight: 600,
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            padding: '0.2rem 0.5rem',
            borderRadius: '999px',
            background: `${color}20`,
            color: color,
            whiteSpace: 'nowrap',
            flexShrink: 0,
          }}
        >
          {label}
        </span>
      </div>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
        {issue.php_version && (
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <span style={{ opacity: 0.6 }}>PHP</span>
            {issue.php_version}
          </span>
        )}
        {issue.os && (
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <span style={{ opacity: 0.6 }}>OS</span>
            {issue.os}
          </span>
        )}
        {issue.github_number && (
          <a
            href={issue.html_url || `#`}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', color: 'var(--color-accent)' }}
          >
            #{issue.github_number}
          </a>
        )}
        <span style={{ opacity: 0.5 }}>
          {new Date(issue.created_at).toLocaleDateString()}
        </span>
      </div>

      <p style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)', lineHeight: 1.5, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
        {issue.body.substring(0, 200)}{issue.body.length > 200 ? '…' : ''}
      </p>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.5rem', paddingTop: '0.5rem', borderTop: '1px solid var(--color-border)', fontSize: '0.7rem', color: 'var(--color-text-muted)' }}>
        <span>Status: {issue.status.replace('_', ' ')}</span>
        <span>Comments: {issue.comments_count}</span>
      </div>
    </article>
  );
}