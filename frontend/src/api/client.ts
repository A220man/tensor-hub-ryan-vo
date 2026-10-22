import axios from 'axios';
import type {
  IssueResponse,
  IssueListResponse,
  IssueCreate,
  IssueUpdate,
  AnalyzeRequest,
  AnalyzeResponse,
  AnalysisResponse,
  TestCaseResponse,
} from '../types/api';

const API_BASE = '/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const issuesApi = {
  list: async (params?: {
    page?: number;
    page_size?: number;
    category?: string;
    status?: string;
  }): Promise<IssueListResponse> => {
    const response = await api.get('/issues', { params });
    return response.data;
  },

  get: async (id: number): Promise<IssueResponse> => {
    const response = await api.get(`/issues/${id}`);
    return response.data;
  },

  create: async (data: IssueCreate): Promise<IssueResponse> => {
    const response = await api.post('/issues', data);
    return response.data;
  },

  update: async (id: number, data: IssueUpdate): Promise<IssueResponse> => {
    const response = await api.patch(`/issues/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/issues/${id}`);
  },

  reanalyze: async (id: number): Promise<IssueResponse> => {
    const response = await api.post(`/issues/${id}/reanalyze`);
    return response.data;
  },

  analyze: async (data: AnalyzeRequest): Promise<AnalyzeResponse> => {
    const response = await api.post('/issues/analyze', data);
    return response.data;
  },
};

export const analysisApi = {
  getByIssue: async (issueId: number): Promise<AnalysisResponse | null> => {
    try {
      const response = await api.get(`/issues/${issueId}/analysis`);
      return response.data;
    } catch {
      return null;
    }
  },
};

export const testCasesApi = {
  getByIssue: async (issueId: number): Promise<TestCaseResponse[]> => {
    const response = await api.get(`/issues/${issueId}/test-cases`);
    return response.data;
  },
};

export default api;