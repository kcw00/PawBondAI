import { useMutation, useQuery } from "@tanstack/react-query";
import { api } from "@/services/api";
import type {
  ChatRequest,
  AnalyzeApplicationRequest,
} from "@/types/api";

// Health check
export const useHealthCheck = () => {
  return useQuery({
    queryKey: ["health"],
    queryFn: () => api.healthCheck(),
    retry: 1,
  });
};

// Chat hooks
export const useSendMessage = () => {
  return useMutation({
    mutationFn: (request: ChatRequest) => api.chat.sendMessage(request),
  });
};

export const useAnalyzeApplication = () => {
  return useMutation({
    mutationFn: (request: AnalyzeApplicationRequest) =>
      api.chat.analyzeApplication(request),
  });
};

// Dogs hooks
export const useDogs = (params?: { limit?: number; offset?: number }) => {
  return useQuery({
    queryKey: ["dogs", params],
    queryFn: () => api.dogs.getAll(params),
  });
};

export const useDog = (id: string) => {
  return useQuery({
    queryKey: ["dog", id],
    queryFn: () => api.dogs.getById(id),
    enabled: !!id,
  });
};

export const useSearchDogs = () => {
  return useMutation({
    mutationFn: (query: string) => api.dogs.search(query),
  });
};

// Applications hooks
export const useApplications = (params?: { limit?: number; offset?: number }) => {
  return useQuery({
    queryKey: ["applications", params],
    queryFn: () => api.applications.getAll(params),
  });
};

export const useApplication = (id: string) => {
  return useQuery({
    queryKey: ["application", id],
    queryFn: () => api.applications.getById(id),
    enabled: !!id,
  });
};

export const useSearchApplications = () => {
  return useMutation({
    mutationFn: (query: string) => api.applications.search(query),
  });
};

// Knowledge hooks
export const useSearchKnowledge = () => {
  return useMutation({
    mutationFn: (query: string) => api.knowledge.search(query),
  });
};

// Case studies hooks
export const useSearchCaseStudies = () => {
  return useMutation({
    mutationFn: (query: string) => api.caseStudies.search(query),
  });
};

// Outcomes hooks
export const useOutcomes = (params?: { limit?: number; offset?: number }) => {
  return useQuery({
    queryKey: ["outcomes", params],
    queryFn: () => api.outcomes.getAll(params),
  });
};

export const useSearchOutcomes = () => {
  return useMutation({
    mutationFn: (query: string) => api.outcomes.search(query),
  });
};

// Analytics hooks
export const useSuccessRates = () => {
  return useQuery({
    queryKey: ["analytics", "success-rates"],
    queryFn: () => api.analytics.getSuccessRates(),
  });
};

export const useMatchingMetrics = () => {
  return useQuery({
    queryKey: ["analytics", "matching-metrics"],
    queryFn: () => api.analytics.getMatchingMetrics(),
  });
};
