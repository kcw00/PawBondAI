import { createContext, useContext, useState, ReactNode } from 'react';

type SearchType = 'behavioral' | 'multiCriteria' | 'similarity' | 'behavioralAnalysis' | null;

interface SearchContextType {
  searchType: SearchType;
  setSearchType: (type: SearchType) => void;
  currentQuery: string;
  setCurrentQuery: (query: string) => void;
  showTrace: boolean;
  setShowTrace: (show: boolean) => void;
}

const SearchContext = createContext<SearchContextType | undefined>(undefined);

export const SearchProvider = ({ children }: { children: ReactNode }) => {
  const [searchType, setSearchType] = useState<SearchType>(null);
  const [currentQuery, setCurrentQuery] = useState<string>('');
  const [showTrace, setShowTrace] = useState<boolean>(false);

  return (
    <SearchContext.Provider value={{ 
      searchType, 
      setSearchType, 
      currentQuery, 
      setCurrentQuery,
      showTrace,
      setShowTrace
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
