import { Search, Zap, Filter } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface SearchExplanation {
  queryBreakdown: string;
  semanticComponent: {
    keyPhrases: string[];
    embeddingSimilarity: number;
  };
  structuredFilters: Array<{ label: string; value: string }>;
  resultsCount: number;
  totalDocuments: number;
  queryTimeMs: number;
}

interface SearchExplanationCardProps {
  explanation: SearchExplanation;
}

export const SearchExplanationCard = ({ explanation }: SearchExplanationCardProps) => {
  return (
    <Card className="p-5 bg-card border-border shadow-sm animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Search className="h-5 w-5 text-primary" />
          <h3 className="text-lg font-bold text-foreground">Search Explanation</h3>
        </div>
        <div className="text-xs text-muted-foreground font-mono">
          Elasticsearch + VertexAI
        </div>
      </div>

      {/* Query Breakdown */}
      <div className="mb-4 p-3 bg-muted/30 rounded-lg border border-border">
        <p className="text-sm text-foreground italic">{explanation.queryBreakdown}</p>
      </div>

      {/* Two Column Layout */}
      <div className="grid md:grid-cols-2 gap-4 mb-4">
        {/* LEFT: Semantic Component */}
        <div className="space-y-3">
          <div className="flex items-center space-x-2">
            <Zap className="h-4 w-4 text-warning" />
            <h4 className="text-sm font-semibold text-foreground">
              Understanding Your Intent
            </h4>
          </div>

          {/* Key Phrases */}
          <div>
            <span className="text-xs text-muted-foreground block mb-2">
              Key phrases extracted:
            </span>
            <div className="flex flex-wrap gap-2">
              {explanation.semanticComponent.keyPhrases.map((phrase, idx) => (
                <Badge
                  key={idx}
                  variant="outline"
                  className="bg-warning/10 text-warning border-warning/20"
                >
                  {phrase}
                </Badge>
              ))}
            </div>
          </div>

          {/* Embedding Similarity */}
          <div className="p-3 bg-warning/5 border border-warning/20 rounded-lg">
            <span className="text-xs text-muted-foreground block mb-1">
              Embedding Similarity Score:
            </span>
            <div className="flex items-center space-x-2">
              <div className="flex-1 bg-muted rounded-full h-2 overflow-hidden">
                <div
                  className="bg-warning h-full transition-all duration-500"
                  style={{
                    width: `${explanation.semanticComponent.embeddingSimilarity * 100}%`,
                  }}
                />
              </div>
              <span className="text-sm font-bold text-warning">
                {(explanation.semanticComponent.embeddingSimilarity * 100).toFixed(0)}%
              </span>
            </div>
          </div>
        </div>

        {/* RIGHT: Structured Filters */}
        <div className="space-y-3">
          <div className="flex items-center space-x-2">
            <Filter className="h-4 w-4 text-success" />
            <h4 className="text-sm font-semibold text-foreground">
              Structured Filters Applied
            </h4>
          </div>

          {/* Filters List */}
          <div className="space-y-2">
            {explanation.structuredFilters.length > 0 ? (
              explanation.structuredFilters.map((filter, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-2 bg-success/5 border border-success/20 rounded"
                >
                  <span className="text-xs font-medium text-muted-foreground">
                    {filter.label}:
                  </span>
                  <span className="text-xs font-semibold text-foreground">
                    {filter.value}
                  </span>
                </div>
              ))
            ) : (
              <p className="text-xs text-muted-foreground italic">
                No structured filters applied - using pure semantic search
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Results Summary */}
      <div className="grid grid-cols-3 gap-4 p-4 bg-gradient-to-br from-primary/5 to-success/5 rounded-lg border border-border">
        <div className="text-center">
          <span className="block text-2xl font-bold text-foreground">
            {explanation.resultsCount}
          </span>
          <span className="text-xs text-muted-foreground">
            Results
          </span>
        </div>
        <div className="text-center">
          <span className="block text-2xl font-bold text-success">
            {explanation.queryTimeMs}ms
          </span>
          <span className="text-xs text-muted-foreground">Query time</span>
        </div>
        <div className="text-center">
          <span className="block text-2xl font-bold text-warning">
            768
          </span>
          <span className="text-xs text-muted-foreground">Vector dims</span>
        </div>
      </div>

      {/* Powered by Badge */}
      <div className="mt-3 pt-3 border-t border-border flex items-center justify-between">
        <span className="text-xs text-muted-foreground font-mono">
          VertexAI text-embedding-005
        </span>
        <Badge
          variant="outline"
          className={cn(
            "text-xs",
            explanation.queryTimeMs < 200
              ? "bg-success/10 text-success border-success/20"
              : "bg-warning/10 text-warning border-warning/20"
          )}
        >
          {explanation.queryTimeMs < 200 ? "⚡ Fast" : "⏱ Moderate"}
        </Badge>
      </div>
    </Card>
  );
};
