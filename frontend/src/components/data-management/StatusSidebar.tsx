import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { RefreshCw, Download, Trash2, FileText } from "lucide-react";

export const StatusSidebar = () => {
  const storageUsed = 2.4;
  const storageTotal = 10;
  const storagePercent = (storageUsed / storageTotal) * 100;

  const recentActivity = [
    { time: "15 min ago", action: "Updated dog profiles", count: 3 },
    { time: "2 hours ago", action: "Uploaded applications", count: 203 },
    { time: "3 days ago", action: "Added medical records", count: 45 }
  ];

  return (
    <div className="sticky top-6 space-y-4">
      <Card className="p-5">
        <div className="flex items-center space-x-2 mb-4">
          <span className="text-lg">📊</span>
          <h3 className="text-base font-bold text-foreground">Index Overview</h3>
        </div>

        <div className="border-b border-border mb-4"></div>

        {/* Elasticsearch Health */}
        <div className="mb-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Elasticsearch Health:</span>
            <div className="flex items-center space-x-1">
              <div className="h-2 w-2 rounded-full bg-success"></div>
              <span className="text-sm font-medium text-success">Healthy</span>
            </div>
          </div>
        </div>

        {/* Total Documents */}
        <div className="mb-4">
          <p className="text-sm font-semibold text-foreground mb-2">Total Documents: 869</p>
          <div className="space-y-1 text-xs text-muted-foreground">
            <div className="flex justify-between">
              <span>├─ Applications:</span>
              <span className="font-medium text-foreground">203</span>
            </div>
            <div className="flex justify-between">
              <span>├─ Dogs:</span>
              <span className="font-medium text-foreground">127</span>
            </div>
            <div className="flex justify-between">
              <span>├─ Medical records:</span>
              <span className="font-medium text-foreground">450</span>
            </div>
            <div className="flex justify-between">
              <span>└─ Case studies:</span>
              <span className="font-medium text-foreground">89</span>
            </div>
          </div>
        </div>

        {/* Storage */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-muted-foreground">Storage Used:</span>
            <span className="text-sm font-medium text-foreground">
              {storageUsed} GB / {storageTotal} GB
            </span>
          </div>
          <Progress value={storagePercent} className="h-2" />
          <p className="text-xs text-muted-foreground mt-1">{storagePercent.toFixed(0)}% used</p>
        </div>

        {/* Last Indexed */}
        <div className="mb-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Last Indexed:</span>
            <span className="text-sm font-medium text-foreground">15 minutes ago</span>
          </div>
        </div>

        <Button variant="outline" size="sm" className="w-full gap-2">
          <RefreshCw className="h-3 w-3" />
          Refresh Now
        </Button>
      </Card>

      {/* Recent Activity */}
      <Card className="p-5">
        <div className="flex items-center space-x-2 mb-4">
          <span className="text-lg">🔄</span>
          <h3 className="text-sm font-bold text-foreground">Recent Activity</h3>
        </div>

        <div className="border-b border-border mb-4"></div>

        <div className="space-y-3">
          {recentActivity.map((activity, idx) => (
            <div key={idx}>
              <p className="text-xs text-muted-foreground mb-1">• {activity.time}</p>
              <p className="text-sm text-foreground">
                {activity.action} ({activity.count} docs)
              </p>
            </div>
          ))}
        </div>

        <Button variant="ghost" size="sm" className="w-full mt-4">
          View Full Activity Log
        </Button>
      </Card>

      {/* Quick Actions */}
      <Card className="p-5">
        <div className="flex items-center space-x-2 mb-4">
          <span className="text-lg">⚙️</span>
          <h3 className="text-sm font-bold text-foreground">Quick Actions</h3>
        </div>

        <div className="border-b border-border mb-4"></div>

        <div className="space-y-2">
          <Button variant="outline" size="sm" className="w-full justify-start gap-2">
            <RefreshCw className="h-3 w-3" />
            Reindex All Data
          </Button>
          <Button variant="outline" size="sm" className="w-full justify-start gap-2">
            <Download className="h-3 w-3" />
            Export Data
          </Button>
          <Button variant="outline" size="sm" className="w-full justify-start gap-2 text-destructive hover:text-destructive">
            <Trash2 className="h-3 w-3" />
            Clear Index
          </Button>
          <Button variant="outline" size="sm" className="w-full justify-start gap-2">
            <FileText className="h-3 w-3" />
            Download Templates
          </Button>
        </div>
      </Card>
    </div>
  );
};
