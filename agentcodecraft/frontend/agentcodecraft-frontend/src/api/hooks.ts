import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './client';
import type {
  RunSummary,
  RunDetail,
  Policy,
  StartRefactorPayload,
  StartRefactorResponse,
  PolicyProfile,
  RefactorRequestPayload,
  RefactorResult,
  ImportPolicyPayload,
  ImportPolicyResponse,
} from './types';

const qk = {
  runs: ['runs'] as const,
  run: (id: string) => ['runs', id] as const,
  policies: ['policies'] as const,
};

export function useRuns() {
  return useQuery<RunSummary[]>({
    queryKey: qk.runs,
    queryFn: async () => {
      const { data } = await apiClient.get<RunSummary[]>('/api/runs');
      return data;
    },
  });
}

export function useRun(runId: string) {
  return useQuery<RunDetail>({
    queryKey: qk.run(runId),
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

      // Stop polling once done/failed
      return stillRunning ? 2000 : false;
    },
  });
}

export function usePolicies() {
  return useQuery<Policy[]>({
    queryKey: qk.policies,
    queryFn: async () => {
      const { data } = await apiClient.get<Policy[]>('/api/policies');
      return data;
    },
  });
}

export function useStartRefactor() {
  const queryClient = useQueryClient();

  return useMutation<StartRefactorResponse, unknown, StartRefactorPayload>({
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

export function usePolicyProfiles() {
  return useQuery({
    queryKey: ['policies'],
    queryFn: async () => {
      const { data } = await apiClient.get<PolicyProfile[]>('/policies');
      return data;
    },
  });
}

export function useRefactor() {
  return useMutation({
    mutationFn: async (payload: RefactorRequestPayload) => {
      const { data } = await apiClient.post<RefactorResult>(
        '/refactor',
        payload
      );
      return data;
    },
  });
}

export function useImportPolicy() {
  return useMutation({
    mutationFn: async (payload: ImportPolicyPayload) => {
      const { data } = await apiClient.post<ImportPolicyResponse>(
        '/policies/import',
        payload
      );
      return data;
    },
  });
}