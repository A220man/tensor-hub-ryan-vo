import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { Dashboard } from './Dashboard';
import { issuesApi } from '../api/client';

vi.mock('../api/client', () => ({
  issuesApi: {
    list: vi.fn(),
  },
}));

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

describe('Dashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows loading state initially', () => {
    (issuesApi.list as unknown as vi.Mock).mockImplementation(() => new Promise(() => {}));
    render(<Dashboard />, { wrapper: createWrapper() });
    expect(screen.getByText('Loading issues…')).toBeInTheDocument();
  });

  it('shows empty state when no issues', async () => {
    (issuesApi.list as unknown as vi.Mock).mockResolvedValue({ items: [], total: 0, page: 1, page_size: 20 });
    render(<Dashboard />, { wrapper: createWrapper() });
    await waitFor(() => expect(screen.getByText('No issues found')).toBeInTheDocument());
  });

  it('renders issue cards when data exists', async () => {
    const mockIssues = [
      {
        id: 1,
        github_number: 7817,
        title: 'JIT segfault',
        body: 'Description',
        html_url: 'https://github.com/php/php-src/issues/7817',
        php_version: '8.1.1',
        os: 'CentOS 7',
        comments_count: 202,
        category: 'segfault',
        status: 'analyzed',
        created_at: '2023-01-15T10:00:00Z',
        updated_at: '2023-01-15T10:00:00Z',
      },
    ];
    (issuesApi.list as unknown as vi.Mock).mockResolvedValue({ items: mockIssues, total: 1, page: 1, page_size: 20 });
    render(<Dashboard />, { wrapper: createWrapper() });
    await waitFor(() => expect(screen.getByText('JIT segfault')).toBeInTheDocument());
  });

  it('shows filter controls', async () => {
    (issuesApi.list as unknown as vi.Mock).mockResolvedValue({ items: [], total: 0, page: 1, page_size: 20 });
    render(<Dashboard />, { wrapper: createWrapper() });
    await waitFor(() => expect(screen.getByText('All Categories')).toBeInTheDocument());
    expect(screen.getByText('All Statuses')).toBeInTheDocument();
  });

  it('shows Import Issue button', async () => {
    (issuesApi.list as unknown as vi.Mock).mockResolvedValue({ items: [], total: 0, page: 1, page_size: 20 });
    render(<Dashboard />, { wrapper: createWrapper() });
    await waitFor(() => expect(screen.getByText('+ Import Issue')).toBeInTheDocument());
  });
});