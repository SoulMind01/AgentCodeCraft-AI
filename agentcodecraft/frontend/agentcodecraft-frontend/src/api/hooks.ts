import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './client';
import type {
  RunSummary,
  RunDetail,
  Policy,
  StartRefactorPayload,
  StartRefactorResponse,
} from './types';

const qk = {
  runs: ['runs'] as const,
  run: (id: string) => ['runs', id] as const,
  policies: ['policies'] as const,
};

export function useRuns() {
  return useQuery({
    queryKey: qk.runs,
    queryFn: async () => {
      const { data } = await apiClient.get<RunSummary[]>('/api/runs');
      return data;
    },
  });
}

export function useRun(runId: string) {
  return useQuery<RunDetail>({
    queryKey: ['runs', runId],
    queryFn: async () => {
      const { data } = await apiClient.get<RunDetail>(`/api/runs/${runId}`);
      return data;
    },
    refetchInterval: (query) => {
      const data = query.state.data;

      // First load → poll until we get data
      if (!data) return 2000;

      // Continue polling while queued or running
      const stillRunning =
        data.status === 'queued' || data.status === 'running';

      return stillRunning ? 2000 : false; // Stop polling once done/failed
    },
  });
}

export function usePolicies() {
  return useQuery({
    queryKey: qk.policies,
    queryFn: async () => {
      const { data } = await apiClient.get<Policy[]>('/api/policies');
      return data;
    },
  });
}

export function useStartRefactor() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: StartRefactorPayload) => {
      const { data } = await apiClient.post<StartRefactorResponse>(
        '/api/refactor',
        payload
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: qk.runs });
    },
  });
}