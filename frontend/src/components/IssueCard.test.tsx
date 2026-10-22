import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { IssueCard } from './IssueCard';
import type { IssueResponse, IssueCategory } from '../types/api';


const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>{children}</BrowserRouter>
    </QueryClientProvider>
  );
};

const mockIssue: IssueResponse = {
  id: 1,
  github_number: 7817,
  title: 'JIT segmentation fault in PHP 8.1',
  body: 'PHP 8.1.0 + 8.1.1 produces segfault, randomly...',
  html_url: 'https://github.com/php/php-src/issues/7817',
  php_version: '8.1.1',
  os: 'CentOS 7',
  comments_count: 202,
  category: 'segfault',
  status: 'analyzed',
  created_at: '2023-01-15T10:00:00Z',
  updated_at: '2023-01-15T10:00:00Z',
};

describe('IssueCard', () => {
  it('renders issue title and category', () => {
    const onClick = vi.fn();
    render(<IssueCard issue={mockIssue} onClick={onClick} />, { wrapper: createWrapper() });
    expect(screen.getByText('JIT segmentation fault in PHP 8.1')).toBeInTheDocument();
    expect(screen.getByText('Segfault')).toBeInTheDocument();
  });

  it('renders PHP version and OS', () => {
    render(<IssueCard issue={mockIssue} onClick={vi.fn()} />, { wrapper: createWrapper() });
    // Match the version badge (contains "8.1.1" but not the full body)
    expect(screen.getByText((content, element) => {
      return content.includes('8.1.1') && element.tagName === 'SPAN';
    })).toBeInTheDocument();
    expect(screen.getByText('CentOS 7')).toBeInTheDocument();
  });

  it('renders GitHub issue number link', () => {
    render(<IssueCard issue={mockIssue} onClick={vi.fn()} />, { wrapper: createWrapper() });
    const link = screen.getByText('#7817');
    expect(link).toBeInTheDocument();
    expect(link).toHaveAttribute('href', 'https://github.com/php/php-src/issues/7817');
  });

  it('calls onClick when clicked', () => {
    const onClick = vi.fn();
    render(<IssueCard issue={mockIssue} onClick={onClick} />, { wrapper: createWrapper() });
    fireEvent.click(screen.getByText('JIT segmentation fault in PHP 8.1'));
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it('shows truncated body', () => {
    const longBody = 'a'.repeat(250);
    const issue = { ...mockIssue, body: longBody };
    render(<IssueCard issue={issue} onClick={vi.fn()} />, { wrapper: createWrapper() });
    expect(screen.getByText('a'.repeat(200) + '…')).toBeInTheDocument();
  });

  it('applies category-specific colors', () => {
    const segfaultIssue = { ...mockIssue, category: 'segfault' as IssueCategory };
    const { container } = render(<IssueCard issue={segfaultIssue} onClick={vi.fn()} />, { wrapper: createWrapper() });
    const badge = container.querySelector('span[style*="rgb(248, 81, 73)"]');
    expect(badge).toBeInTheDocument();
  });
});