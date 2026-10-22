import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { issuesApi } from '../api/client';
import type { IssueResponse, IssueListResponse, IssueCreate, IssueUpdate, AnalyzeRequest, AnalyzeResponse } from '../types/api';

export function useIssues(page = 1, pageSize = 20, category?: string, status?: string) {
  return useQuery<IssueListResponse>({
    queryKey: ['issues', page, pageSize, category, status],
    queryFn: () => issuesApi.list({ page, page_size: pageSize, category, status }),
  });
}

export function useIssue(id: number) {
  return useQuery<IssueResponse>({
    queryKey: ['issues', id],
    queryFn: () => issuesApi.get(id),
    enabled: !!id,
  });
}

export function useCreateIssue() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: IssueCreate) => issuesApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['issues'] });
    },
  });
}

export function useUpdateIssue() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: IssueUpdate }) => issuesApi.update(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['issues'] });
      queryClient.invalidateQueries({ queryKey: ['issues', id] });
    },
  });
}

export function useDeleteIssue() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => issuesApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['issues'] });
    },
  });
}

export function useReanalyzeIssue() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => issuesApi.reanalyze(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['issues'] });
      queryClient.invalidateQueries({ queryKey: ['issues', id] });
    },
  });
}

export function useAnalyzeIssue() {
  return useMutation<AnalyzeResponse, Error, AnalyzeRequest>({
    mutationFn: (data) => issuesApi.analyze(data),
  });
}