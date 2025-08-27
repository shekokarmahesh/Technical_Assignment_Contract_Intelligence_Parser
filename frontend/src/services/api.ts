import { 
  API_BASE_URL, 
  Contract, 
  ContractDetails, 
  ContractListResponse, 
  UploadResponse,
  ContractStats,
  HealthCheckResponse,
  APIError
} from './types';

class APIService {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  private async fetchWithErrorHandling<T>(
    url: string, 
    options?: RequestInit
  ): Promise<T> {
    try {
      const response = await fetch(`${this.baseURL}${url}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
        ...options,
      });

      if (!response.ok) {
        const errorData: APIError = await response.json().catch(() => ({
          detail: `HTTP ${response.status}: ${response.statusText}`
        }));
        throw new Error(errorData.detail);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('An unexpected error occurred');
    }
  }

  // Health Check
  async healthCheck(): Promise<HealthCheckResponse> {
    return this.fetchWithErrorHandling<HealthCheckResponse>('/health');
  }

  // Contract Upload
  async uploadContract(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${this.baseURL}/contracts/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData: APIError = await response.json().catch(() => ({
          detail: `HTTP ${response.status}: ${response.statusText}`
        }));
        throw new Error(errorData.detail);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Upload failed');
    }
  }

  // Get Contract Status
  async getContractStatus(contractId: string): Promise<Contract> {
    return this.fetchWithErrorHandling<Contract>(`/contracts/${contractId}/status`);
  }

  // Get Contract Details
  async getContractDetails(contractId: string): Promise<ContractDetails> {
    return this.fetchWithErrorHandling<ContractDetails>(`/contracts/${contractId}`);
  }

  // List Contracts
  async listContracts(params?: {
    page?: number;
    limit?: number;
    status?: string;
    sort_by?: string;
    sort_order?: 'asc' | 'desc';
  }): Promise<ContractListResponse> {
    const searchParams = new URLSearchParams();
    
    if (params?.page) searchParams.set('page', params.page.toString());
    if (params?.limit) searchParams.set('limit', params.limit.toString());
    if (params?.status) searchParams.set('status', params.status);
    if (params?.sort_by) searchParams.set('sort_by', params.sort_by);
    if (params?.sort_order) searchParams.set('sort_order', params.sort_order);

    const queryString = searchParams.toString();
    const url = queryString ? `/contracts?${queryString}` : '/contracts';

    return this.fetchWithErrorHandling<ContractListResponse>(url);
  }

  // Download Contract
  async downloadContract(contractId: string): Promise<Blob> {
    try {
      const response = await fetch(`${this.baseURL}/contracts/${contractId}/download`);

      if (!response.ok) {
        const errorData: APIError = await response.json().catch(() => ({
          detail: `HTTP ${response.status}: ${response.statusText}`
        }));
        throw new Error(errorData.detail);
      }

      return await response.blob();
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Download failed');
    }
  }

  // Delete Contract
  async deleteContract(contractId: string): Promise<{ message: string; contract_id: string }> {
    return this.fetchWithErrorHandling(`/contracts/${contractId}`, {
      method: 'DELETE',
    });
  }

  // Get Contract Statistics
  async getContractStats(): Promise<ContractStats> {
    return this.fetchWithErrorHandling<ContractStats>('/contracts/stats');
  }

  // Utility method to trigger file download
  downloadFile(blob: Blob, filename: string) {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  }
}

// Create singleton instance
export const apiService = new APIService();
export default apiService;
