import { Zap, Activity, Heart } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export const MetricBanner = () => {
  return (
    <div className="bg-gradient-to-r from-primary/20 via-success/20 to-primary/20 border-b border-border px-6 py-3">
      <div className="flex items-center justify-between max-w-7xl mx-auto">
        <div className="flex items-center gap-3">
          {/* PawBondAI Mascot - Paw + Heart */}
          <div className="relative flex-shrink-0">
            <div className="relative w-8 h-8">
              <Heart className="h-5 w-5 text-secondary absolute top-0 left-0 fill-secondary/20" />
              <div className="absolute bottom-0 right-0 w-4 h-4 rounded-full bg-success/20 border-2 border-success" />
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <Zap className="h-4 w-4 text-success" />
            <span className="text-sm font-semibold text-foreground">
              Elastic + Google AI Powering Adoption Intelligence
            </span>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <Badge variant="outline" className="bg-success/10 text-success border-success/20 text-xs">
            <Activity className="h-3 w-3 mr-1" />
            Live
          </Badge>
        </div>
      </div>
    </div>
  );
};
