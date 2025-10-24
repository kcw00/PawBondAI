import { createContext, useContext, useState, ReactNode } from 'react';

type SearchType = 'behavioral' | 'multiCriteria' | 'similarity' | 'behavioralAnalysis' | null;

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  intent?: string;
  metadata?: any;
}

interface TraceStep {
  id: string;
  label: string;
  status: 'complete' | 'processing' | 'pending';
  duration?: number;
  details?: string;
  data?: any;
}

interface TraceData {
  steps: TraceStep[];
  total_duration_ms: number;
  query: string;
}

interface SearchContextType {
  searchType: SearchType;
  setSearchType: (type: SearchType) => void;
  currentQuery: string;
  setCurrentQuery: (query: string) => void;
  showTrace: boolean;
  setShowTrace: (show: boolean) => void;
  loadedSessionId: string | null;
  setLoadedSessionId: (sessionId: string | null) => void;
  loadedMessages: ChatMessage[];
  setLoadedMessages: (messages: ChatMessage[]) => void;
  traceData: TraceData | null;
  setTraceData: (trace: TraceData | null) => void;
}

const SearchContext = createContext<SearchContextType | undefined>(undefined);

export const SearchProvider = ({ children }: { children: ReactNode }) => {
  const [searchType, setSearchType] = useState<SearchType>(null);
  const [currentQuery, setCurrentQuery] = useState<string>('');
  const [showTrace, setShowTrace] = useState<boolean>(false);
  const [loadedSessionId, setLoadedSessionId] = useState<string | null>(null);
  const [loadedMessages, setLoadedMessages] = useState<ChatMessage[]>([]);
  const [traceData, setTraceData] = useState<TraceData | null>(null);

  return (
    <SearchContext.Provider value={{
      searchType,
      setSearchType,
      currentQuery,
      setCurrentQuery,
      showTrace,
      setShowTrace,
      loadedSessionId,
      setLoadedSessionId,
      loadedMessages,
      setLoadedMessages,
      traceData,
      setTraceData
    }}>
      {children}
    </SearchContext.Provider>
  );
};

export const useSearch = () => {
  const context = useContext(SearchContext);
  if (context === undefined) {
    throw new Error('useSearch must be used within a SearchProvider');
  }
  return context;
};
