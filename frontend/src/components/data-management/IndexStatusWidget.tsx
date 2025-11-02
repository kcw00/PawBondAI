import { useState, useEffect } from "react";
import { Database, RefreshCw, Activity } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { ScrollArea } from "@/components/ui/scroll-area";
import { toast } from "sonner";
import { API_BASE_URL } from "@/services/api";

interface IndexStats {
  total_documents: number;
  applications_count: number;
  dogs_count: number;
  outcomes_count: number;
  medical_documents_count: number;
  recent_activity: Array<{
    type: string;
    count: number;
    timestamp: string | null;
  }>;
  health_status: string;
}

interface IndexStatusWidgetProps {
  refreshTrigger?: number;
}

export const IndexStatusWidget = ({ refreshTrigger }: IndexStatusWidgetProps) => {
  const [open, setOpen] = useState(false);
  const [stats, setStats] = useState<IndexStats | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/analytics/index-stats`);
      if (!response.ok) throw new Error('Failed to fetch stats');
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error fetching index stats:', error);
      toast.error('Failed to fetch index statistics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, [refreshTrigger]);

  const formatTimestamp = (timestamp: string | null) => {
    if (!timestamp) return 'N/A';
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) return `${diffMins} min ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
  };

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
          {stats?.total_documents || 0}
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
                    {stats?.health_status === 'healthy' ? '🟢 Healthy' : '🔴 Empty'}
                  </Badge>
                </div>

                <div className="space-y-3">
                  <div>
                    <p className="text-2xl font-bold text-foreground">{stats?.total_documents || 0}</p>
                    <p className="text-xs text-muted-foreground">Total Documents</p>
                  </div>

                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">├─ Applications:</span>
                      <span className="font-semibold text-foreground">{stats?.applications_count || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">├─ Dogs:</span>
                      <span className="font-semibold text-foreground">{stats?.dogs_count || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">├─ Outcomes:</span>
                      <span className="font-semibold text-foreground">{stats?.outcomes_count || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">└─ Medical Docs:</span>
                      <span className="font-semibold text-foreground">{stats?.medical_documents_count || 0}</span>
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
                    <span className="font-medium text-foreground">{stats?.total_documents || 0}</span>
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
                  <p className="text-xs text-muted-foreground mb-2">
                    {stats?.recent_activity?.[0]?.timestamp 
                      ? `Last indexed: ${formatTimestamp(stats.recent_activity[0].timestamp)}` 
                      : 'No recent activity'}
                  </p>
                  <Button 
                    size="sm" 
                    variant="outline"
                    className="w-full border-[#718355] text-[#718355] hover:bg-[#718355] hover:text-white"
                    onClick={fetchStats}
                    disabled={loading}
                  >
                    <RefreshCw className={`h-3 w-3 mr-2 ${loading ? 'animate-spin' : ''}`} />
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
                  {stats?.recent_activity && stats.recent_activity.length > 0 ? (
                    stats.recent_activity.map((activity, idx) => (
                      <div key={idx}>
                        <p className="text-xs text-muted-foreground mb-1">
                          • {formatTimestamp(activity.timestamp)}
                        </p>
                        <p className="text-sm text-foreground">
                          Indexed {activity.count} {activity.type}
                        </p>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-muted-foreground">No recent activity</p>
                  )}
                </div>
              </div>
            </div>
          </ScrollArea>
        </SheetContent>
      </Sheet>
    </>
  );
};
