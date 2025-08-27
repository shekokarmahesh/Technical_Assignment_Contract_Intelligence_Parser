import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useToast } from '@/hooks/use-toast';
import apiService from './api';
import type { Contract, ContractDetails, ContractListResponse, ContractStats } from './types';

// Query Keys
export const queryKeys = {
  health: ['health'] as const,
  contracts: ['contracts'] as const,
  contractList: (params?: any) => ['contracts', 'list', params] as const,
  contractDetails: (id: string) => ['contracts', 'details', id] as const,
  contractStatus: (id: string) => ['contracts', 'status', id] as const,
  contractStats: ['contracts', 'stats'] as const,
};

// Health Check Hook
export const useHealthCheck = () => {
  return useQuery({
    queryKey: queryKeys.health,
    queryFn: apiService.healthCheck,
    retry: 3,
    refetchInterval: 30000, // Check every 30 seconds
  });
};

// Contract Upload Hook
export const useUploadContract = () => {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (file: File) => apiService.uploadContract(file),
    onSuccess: (data) => {
      toast({
        title: "Upload Successful",
        description: `Contract ${data.contract_id} is now being processed.`,
      });
      // Invalidate contract list to show new contract
      queryClient.invalidateQueries({ queryKey: queryKeys.contracts });
    },
    onError: (error: Error) => {
      toast({
        title: "Upload Failed",
        description: error.message,
        variant: "destructive",
      });
    },
  });
};

// Contract List Hook
export const useContractList = (params?: {
  page?: number;
  limit?: number;
  status?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}) => {
  return useQuery({
    queryKey: queryKeys.contractList(params),
    queryFn: () => apiService.listContracts(params),
    placeholderData: (previousData) => previousData, // Keep previous data while fetching new page
  });
};

// Contract Status Hook (with polling for processing contracts)
export const useContractStatus = (contractId: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: queryKeys.contractStatus(contractId),
    queryFn: () => apiService.getContractStatus(contractId),
    enabled,
    refetchInterval: (query) => {
      // Poll every 2 seconds if contract is processing or pending
      const data = query.state.data;
      if (data?.status === 'processing' || data?.status === 'pending') {
        return 2000;
      }
      return false; // Stop polling when completed or failed
    },
    refetchIntervalInBackground: true,
  });
};

// Contract Details Hook
export const useContractDetails = (contractId: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: queryKeys.contractDetails(contractId),
    queryFn: () => apiService.getContractDetails(contractId),
    enabled,
    retry: (failureCount, error) => {
      // Don't retry if contract is not ready (400 error)
      if (error.message.includes('not completed')) {
        return false;
      }
      return failureCount < 3;
    },
  });
};

// Contract Download Hook
export const useDownloadContract = () => {
  const { toast } = useToast();

  return useMutation({
    mutationFn: ({ contractId, filename }: { contractId: string; filename: string }) =>
      apiService.downloadContract(contractId).then(blob => ({ blob, filename })),
    onSuccess: ({ blob, filename }) => {
      apiService.downloadFile(blob, filename);
      toast({
        title: "Download Started",
        description: `Downloading ${filename}`,
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Download Failed",
        description: error.message,
        variant: "destructive",
      });
    },
  });
};

// Contract Delete Hook
export const useDeleteContract = () => {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (contractId: string) => apiService.deleteContract(contractId),
    onSuccess: (data) => {
      toast({
        title: "Contract Deleted",
        description: `Contract ${data.contract_id} has been deleted successfully.`,
      });
      // Invalidate and refetch contract list
      queryClient.invalidateQueries({ queryKey: queryKeys.contracts });
    },
    onError: (error: Error) => {
      toast({
        title: "Delete Failed",
        description: error.message,
        variant: "destructive",
      });
    },
  });
};

// Contract Statistics Hook
export const useContractStats = () => {
  return useQuery({
    queryKey: queryKeys.contractStats,
    queryFn: apiService.getContractStats,
    refetchInterval: 60000, // Refresh every minute
  });
};

// Utility hook to refresh contract data
export const useRefreshContract = () => {
  const queryClient = useQueryClient();

  return {
    refreshStatus: (contractId: string) => {
      queryClient.invalidateQueries({ 
        queryKey: queryKeys.contractStatus(contractId) 
      });
    },
    refreshDetails: (contractId: string) => {
      queryClient.invalidateQueries({ 
        queryKey: queryKeys.contractDetails(contractId) 
      });
    },
    refreshList: () => {
      queryClient.invalidateQueries({ 
        queryKey: queryKeys.contracts 
      });
    },
    refreshAll: () => {
      queryClient.invalidateQueries({ 
        queryKey: queryKeys.contracts 
      });
    },
  };
};
