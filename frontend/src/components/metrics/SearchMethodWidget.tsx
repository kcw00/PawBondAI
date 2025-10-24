import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Brain, Filter, Sparkles } from "lucide-react";

export const SearchMethodWidget = () => {
  return (
    <Card className="p-4 bg-gradient-to-br from-primary/5 to-success/5 border-border">
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-primary" />
            <h3 className="text-sm font-semibold text-foreground">Hybrid Search Method</h3>
          </div>
          <Badge variant="outline" className="bg-success/10 text-success border-success/20 text-xs">
            RRF Combined
          </Badge>
        </div>

        {/* Search Weights */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Brain className="h-4 w-4 text-warning" />
              <span className="text-sm text-foreground font-medium">Semantic</span>
            </div>
            <span className="text-lg font-bold text-warning">70%</span>
          </div>
          <div className="w-full bg-muted rounded-full h-2">
            <div className="bg-warning h-full rounded-full transition-all duration-500" style={{ width: '70%' }} />
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4 text-success" />
              <span className="text-sm text-foreground font-medium">Structured</span>
            </div>
            <span className="text-lg font-bold text-success">30%</span>
          </div>
          <div className="w-full bg-muted rounded-full h-2">
            <div className="bg-success h-full rounded-full transition-all duration-500" style={{ width: '30%' }} />
          </div>
        </div>

        {/* Model Info */}
        <div className="pt-3 border-t border-border">
          <div className="flex items-center justify-between text-xs">
            <span className="text-muted-foreground">Model:</span>
            <span className="font-mono text-foreground">VertexAI text-embedding-005</span>
          </div>
          <div className="flex items-center justify-between text-xs mt-1">
            <span className="text-muted-foreground">Dimensions:</span>
            <span className="font-mono text-foreground">768-dim</span>
          </div>
        </div>
      </div>
    </Card>
  );
};
