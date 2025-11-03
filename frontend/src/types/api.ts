// API Request/Response Types matching backend schemas

export interface TraceStep {
  id: string;
  label: string;
  status: 'complete' | 'processing' | 'pending';
  duration?: number;
  details?: string;
  data?: any;
}

export interface TraceData {
  steps: TraceStep[];
  total_duration_ms: number;
  query: string;
}

export interface ChatRequest {
  message: string;
  context?: Record<string, any>;
}

export interface ChatResponse {
  success: boolean;
  intent: string;
  response: any;
  session_id?: string;
  trace?: TraceData;
}

export interface AnalyzeApplicationRequest {
  application_text: string;
}

export interface SimilarAdopter {
  name: string;
  similarity: number;
  dogName: string;
  dogAge: number;
  adoptionDate: string;
  outcome: "successful" | "returned";
  traits: string[];
  followUp: string[];
  successFactors: string[];
}

export interface DogMatch {
  id: string;
  name: string;
  breed: string;
  age: number;
  matchScore: number;
  reasons: string[];
  similarPairing?: string;
}

export interface ApplicationAnalysis {
  applicantName: string;
  strengths: string[];
  experienceLevel: string;
  bestSuitedFor: string[];
  similarAdopters: SimilarAdopter[];
  successRate: number;
  successFactors: Record<string, number>;
  recommendedDogs: DogMatch[];
}

export interface AnalyzeApplicationResponse {
  success: boolean;
  text?: string;  // Formatted ChatGPT-style summary from Gemini
  analysis: ApplicationAnalysis;
  trace?: TraceData;
}

export interface HealthCheckResponse {
  status: string;
  message: string;
  cluster_status?: string;
  number_of_nodes?: number;
  active_shards?: number;
}
