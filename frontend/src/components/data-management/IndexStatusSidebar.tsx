import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { RefreshCw, Activity } from "lucide-react";

export const IndexStatusSidebar = () => {
  return (
    <div className="space-y-4">
      <Card className="p-4 bg-white border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-bold text-foreground">📊 Elasticsearch Index Status</h3>
          <Badge variant="secondary" className="bg-[#6a994e]/20 text-[#6a994e]">
            🟢 Healthy
          </Badge>
        </div>

        <div className="space-y-3">
          <div>
            <p className="text-2xl font-bold text-foreground">419</p>
            <p className="text-xs text-muted-foreground">Total Documents</p>
          </div>

          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">├─ Applications:</span>
              <span className="font-semibold text-foreground">203</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">├─ Dogs:</span>
              <span className="font-semibold text-foreground">127</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">└─ Success cases:</span>
              <span className="font-semibold text-foreground">89</span>
            </div>
          </div>

          <div className="pt-3 border-t border-gray-200">
            <p className="text-sm font-semibold text-foreground mb-2">Vector Embeddings</p>
            <div className="space-y-1 text-xs">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Total embeddings:</span>
                <span className="font-medium text-foreground">392</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Model:</span>
                <span className="font-medium text-foreground">text-embedding-004</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Dimensions:</span>
                <span className="font-medium text-foreground">768</span>
              </div>
            </div>
          </div>

          <div className="pt-3 border-t border-gray-200">
            <p className="text-xs text-muted-foreground mb-2">Last indexed: 15 min ago</p>
            <Button 
              size="sm" 
              variant="outline"
              className="w-full border-[#718355] text-[#718355] hover:bg-[#718355] hover:text-white"
            >
              <RefreshCw className="h-3 w-3 mr-2" />
              Refresh Status
            </Button>
          </div>
        </div>
      </Card>

      <Card className="p-4 bg-white border-gray-200">
        <div className="flex items-center mb-3">
          <Activity className="h-4 w-4 text-[#718355] mr-2" />
          <h3 className="text-sm font-bold text-foreground">Recent Activity</h3>
        </div>

        <div className="space-y-3">
          <div>
            <p className="text-xs text-muted-foreground mb-1">• 15 min ago</p>
            <p className="text-sm text-foreground">Uploaded 50 applications</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground mb-1">• 2 hours ago</p>
            <p className="text-sm text-foreground">Indexed 3 dog profiles</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground mb-1">• 5 hours ago</p>
            <p className="text-sm text-foreground">Added 2 success cases</p>
          </div>
        </div>

        <Button 
          size="sm" 
          variant="ghost"
          className="w-full mt-3 text-[#718355] hover:bg-[#718355]/10"
        >
          View Full Log
        </Button>
      </Card>
    </div>
  );
};
