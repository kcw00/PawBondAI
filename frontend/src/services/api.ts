import type {
  ChatRequest,
  ChatResponse,
  AnalyzeApplicationRequest,
  AnalyzeApplicationResponse,
  HealthCheckResponse,
} from "@/types/api";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
    public data?: any
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        errorData.detail || `HTTP ${response.status}: ${response.statusText}`,
        response.status,
        errorData
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(
      error instanceof Error ? error.message : "Network error occurred",
      undefined,
      error
    );
  }
}

export const api = {
  // Health check
  healthCheck: () => fetchApi<HealthCheckResponse>("/health"),

  // Chat endpoints
  chat: {
    sendMessage: (request: ChatRequest) =>
      fetchApi<ChatResponse>("/chat/message", {
        method: "POST",
        body: JSON.stringify(request),
      }),

    analyzeApplication: (request: AnalyzeApplicationRequest) =>
      fetchApi<AnalyzeApplicationResponse>("/chat/analyze-application", {
        method: "POST",
        body: JSON.stringify(request),
      }),

    getSearchInsights: (queryId: string) =>
      fetchApi<any>(`/chat/search-insights/${queryId}`),
  },

  // Dogs endpoints
  dogs: {
    getAll: (params?: { limit?: number; offset?: number }) => {
      const searchParams = new URLSearchParams();
      if (params?.limit) searchParams.set("limit", params.limit.toString());
      if (params?.offset) searchParams.set("offset", params.offset.toString());
      const query = searchParams.toString();
      return fetchApi<any>(`/dogs${query ? `?${query}` : ""}`);
    },

    getById: (id: string) => fetchApi<any>(`/dogs/${id}`),

    search: (query: string) =>
      fetchApi<any>("/dogs/search", {
        method: "POST",
        body: JSON.stringify({ query }),
      }),
  },

  // Applications endpoints
  applications: {
    getAll: (params?: { limit?: number; offset?: number }) => {
      const searchParams = new URLSearchParams();
      if (params?.limit) searchParams.set("limit", params.limit.toString());
      if (params?.offset) searchParams.set("offset", params.offset.toString());
      const query = searchParams.toString();
      return fetchApi<any>(`/applications${query ? `?${query}` : ""}`);
    },

    getById: (id: string) => fetchApi<any>(`/applications/${id}`),

    search: (query: string) =>
      fetchApi<any>("/applications/search", {
        method: "POST",
        body: JSON.stringify({ query }),
      }),
  },

  // Knowledge endpoints
  knowledge: {
    search: (query: string) =>
      fetchApi<any>("/knowledge/search", {
        method: "POST",
        body: JSON.stringify({ query }),
      }),
  },

  // Case studies endpoints
  caseStudies: {
    search: (query: string) =>
      fetchApi<any>("/case-studies/search", {
        method: "POST",
        body: JSON.stringify({ query }),
      }),
  },

  // Outcomes endpoints
  outcomes: {
    getAll: (params?: { limit?: number; offset?: number }) => {
      const searchParams = new URLSearchParams();
      if (params?.limit) searchParams.set("limit", params.limit.toString());
      if (params?.offset) searchParams.set("offset", params.offset.toString());
      const query = searchParams.toString();
      return fetchApi<any>(`/outcomes${query ? `?${query}` : ""}`);
    },

    search: (query: string) =>
      fetchApi<any>("/outcomes/search", {
        method: "POST",
        body: JSON.stringify({ query }),
      }),
  },

  // Analytics endpoints
  analytics: {
    getSuccessRates: () => fetchApi<any>("/analytics/success-rates"),
    getMatchingMetrics: () => fetchApi<any>("/analytics/matching-metrics"),
  },
};

export { ApiError };
