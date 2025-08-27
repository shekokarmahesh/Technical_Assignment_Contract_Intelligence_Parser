// API Configuration
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

// API Response Types
export interface Contract {
  contract_id: string;
  filename: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  score?: number;
  upload_date: string;
  updated_at: string;
  file_size: number;
  gaps_count?: number;
  error?: string;
  processing_completed_at?: string;
}

export interface ContractDetails extends Contract {
  extracted_data: ExtractedData;
  gaps: Gap[];
  confidence_scores: ConfidenceScores;
}

export interface ExtractedData {
  parties: Party[];
  financial_details: FinancialDetails;
  payment_structure: PaymentStructure;
  sla_terms: SLATerms;
  contact_information: ContactInfo;
  account_information: AccountInfo;
  revenue_classification: RevenueClassification;
  raw_text_length: number;
  extraction_metadata: ExtractionMetadata;
}

export interface Party {
  name: string;
  role: string;
  legal_entity?: string;
  confidence: number;
}

export interface FinancialDetails {
  total_value?: string;
  total_value_confidence?: number;
  currency?: string;
  line_items?: LineItem[];
  tax_information?: TaxInfo;
}

export interface LineItem {
  description: string;
  quantity: number;
  unit_price: string;
  total: string;
}

export interface TaxInfo {
  rate: string;
  confidence: number;
}

export interface PaymentStructure {
  terms?: string;
  terms_confidence?: number;
  schedule?: string;
  schedule_confidence?: number;
  method?: string;
  method_confidence?: number;
}

export interface SLATerms {
  response_time?: string;
  response_time_confidence?: number;
  uptime_guarantee?: string;
  uptime_confidence?: number;
  penalties?: string;
  penalties_confidence?: number;
}

export interface ContactInfo {
  emails?: string[];
  phones?: string[];
}

export interface AccountInfo {
  account_number?: string;
  account_confidence?: number;
  billing_address?: string;
}

export interface RevenueClassification {
  type: string;
  billing_cycle?: string;
  renewal_terms?: string;
}

export interface ExtractionMetadata {
  total_pages: number;
  extraction_method: string;
  text_length: number;
}

export interface Gap {
  field: string;
  importance: string;
  status: string;
  description: string;
}

export interface ConfidenceScores {
  parties?: number;
  financial_details?: number;
  payment_structure?: number;
  sla_terms?: number;
  account_information?: number;
}

export interface ContractListResponse {
  contracts: Contract[];
  pagination: {
    current_page: number;
    total_pages: number;
    total_count: number;
    page_size: number;
    has_next: boolean;
    has_prev: boolean;
  };
  filters: {
    status: string | null;
    sort_by: string;
    sort_order: string;
  };
}

export interface UploadResponse {
  contract_id: string;
  message: string;
  filename: string;
}

export interface ContractStats {
  total_contracts: number;
  completed_contracts: number;
  completion_rate: number;
  average_score: number;
  status_breakdown: Record<string, number>;
  timestamp: string;
}

export interface HealthCheckResponse {
  status: string;
  service: string;
  timestamp: string;
}

export interface APIError {
  detail: string;
}
