import { Search, Lightbulb, Activity } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useSearch } from "@/contexts/SearchContext";
import { queryInsights } from "@/data/mockAdopterData";
import { behavioralSearchInsights } from "@/data/mockBehavioralData";
import { SearchMethodWidget } from "./metrics/SearchMethodWidget";

export const RightSidebar = () => {
  const { searchType } = useSearch();
  
  // Get the appropriate query insights based on context
  const getQueryData = () => {
    if (searchType === 'behavioralAnalysis') return behavioralSearchInsights;
    if (searchType === 'behavioral') return queryInsights.behavioral;
    if (searchType === 'multiCriteria') return queryInsights.multiCriteria;
    if (searchType === 'similarity') return queryInsights.similarity;
    
    // Default to behavioral for initial display
    return queryInsights.behavioral;
  };

  const { parsedQuery, semanticSearch, structuredSearch, execution } = getQueryData();

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

        {/* Search Query Card */}
        <Card className="p-4 bg-card border-border">
          <div className="flex items-center mb-3">
            <Search className="h-4 w-4 text-primary mr-2" />
            <h4 className="text-sm font-semibold text-foreground">Query Analysis</h4>
          </div>
          
          <div className="space-y-2 text-xs text-foreground">
            <p>• Looking for: <span className="font-semibold">"{parsedQuery.entities.join('", "')}"</span></p>
            <p>• Intent: <span className="font-semibold">{parsedQuery.intent}</span></p>
          </div>
        </Card>

        {/* Results Card */}
        <Card className="p-4 bg-card border-border">
          <div className="flex items-center mb-3">
            <Activity className="h-4 w-4 text-success mr-2" />
            <h4 className="text-sm font-semibold text-foreground">Results</h4>
          </div>

          <div className="space-y-3">
            <div className="flex justify-between text-xs">
              <span className="text-muted-foreground">Found:</span>
              <span className="font-semibold text-success">{execution.results} matches</span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-muted-foreground">Search time:</span>
              <span className="font-semibold text-success">{execution.queryTime}</span>
            </div>

            <div className="pt-3 border-t border-border">
              <p className="text-xs font-semibold text-foreground mb-2">Top matches:</p>
              <div className="space-y-1.5">
                {execution.topScores.map((item, idx) => (
                  <div key={idx} className="flex justify-between items-center p-2 bg-muted/30 rounded">
                    <span className="text-xs text-foreground">{item.name}</span>
                    <span className="text-xs font-bold text-success">{item.score}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};
