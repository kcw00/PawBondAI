import { Search, Lightbulb, Activity } from "lucide-react";
import { Card } from "@/components/ui/card";
import { useSearch } from "@/contexts/SearchContext";
import { SearchMethodWidget } from "./metrics/SearchMethodWidget";

export const RightSidebar = () => {
  const { searchType } = useSearch();

  return (
    <div className="flex flex-col h-full bg-background">
      {/* Header */}
      <div className="p-4 border-b border-border flex-shrink-0">
        <h2 className="text-lg font-bold text-foreground flex items-center gap-2">
          <Lightbulb className="h-5 w-5 text-warning" />
          Search Insights
        </h2>
        <p className="text-xs text-muted-foreground mt-1">
          Elastic + Google AI Analytics
        </p>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Search Method Widget */}
        <SearchMethodWidget />

        {/* Placeholder message */}
        <Card className="p-4 bg-card border-border">
          <div className="flex items-center mb-3">
            <Search className="h-4 w-4 text-primary mr-2" />
            <h4 className="text-sm font-semibold text-foreground">Search Analytics</h4>
          </div>

          <div className="space-y-2 text-xs text-muted-foreground">
            <p>Real-time search insights will appear here when using the Real API mode.</p>
            <p className="pt-2">Enable Real API mode and perform a search to see live analytics from your Elasticsearch cluster.</p>
          </div>
        </Card>
      </div>
    </div>
  );
};
