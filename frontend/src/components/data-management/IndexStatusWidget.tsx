import { useState } from "react";
import { Database, RefreshCw, Activity } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { ScrollArea } from "@/components/ui/scroll-area";

export const IndexStatusWidget = () => {
  const [open, setOpen] = useState(false);

  return (
    <>
      {/* Floating Widget Button */}
      <Button
        onClick={() => setOpen(true)}
        className="fixed bottom-6 right-6 h-12 gap-2 bg-card hover:bg-card/90 text-foreground border border-border shadow-lg z-50"
        variant="outline"
      >
        <Database className="h-4 w-4" />
        <span className="text-sm font-medium">Index Status</span>
        <Badge variant="secondary" className="bg-[#6a994e]/20 text-[#6a994e] ml-1">
          419
        </Badge>
      </Button>

      {/* Drawer */}
      <Sheet open={open} onOpenChange={setOpen}>
        <SheetContent side="right" className="w-[400px] sm:w-[400px] overflow-hidden flex flex-col">
          <SheetHeader>
            <SheetTitle className="flex items-center gap-2">
              <Database className="h-5 w-5" />
              Elasticsearch Index Status
            </SheetTitle>
          </SheetHeader>

          <ScrollArea className="flex-1 pr-4">
            <div className="space-y-4 py-4">
              {/* Health Status Card */}
              <div className="p-4 bg-muted/30 rounded-lg border border-border">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-bold text-foreground">Overall Health</h3>
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
                </div>
              </div>

              {/* Vector Embeddings Card */}
              <div className="p-4 bg-muted/30 rounded-lg border border-border">
                <p className="text-sm font-semibold text-foreground mb-3">Vector Embeddings</p>
                <div className="space-y-2 text-xs">
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

                <div className="mt-4 pt-3 border-t border-border">
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

              {/* Recent Activity Card */}
              <div className="p-4 bg-muted/30 rounded-lg border border-border">
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
              </div>
            </div>
          </ScrollArea>
        </SheetContent>
      </Sheet>
    </>
  );
};
