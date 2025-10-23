import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { SearchProvider } from "./contexts/SearchContext";
import Index from "./pages/Index";
import NotFound from "./pages/NotFound";
import CardShowcase from "./pages/CardShowcase";
import DataManagementPage from "./pages/DataManagementPage";
import DogProfilePage from "./pages/DogProfilePage";
import ChatHistoryPage from "./pages/ChatHistoryPage";

const queryClient = new QueryClient();

const App = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <SearchProvider>
          <Toaster />
          <Sonner />
          <BrowserRouter>
            <Routes>
              <Route path="/" element={<Index />} />
              <Route path="/data-management" element={<DataManagementPage />} />
              <Route path="/chat-history" element={<ChatHistoryPage />} />
              <Route path="/card-showcase" element={<CardShowcase />} />
              <Route path="/dogs/:id" element={<DogProfilePage />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </BrowserRouter>
        </SearchProvider>
      </TooltipProvider>
    </QueryClientProvider>
  );
};

export default App;
