import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Activity, Zap, Globe, TrendingUp } from "lucide-react";

interface MetricCardProps {
  icon: React.ReactNode;
  label: string;
  value: string;
  subtext?: string;
  trend?: "up" | "stable";
}

const MetricCard = ({ icon, label, value, subtext, trend }: MetricCardProps) => {
  return (
    <Card className="p-4 bg-card border-border hover:shadow-md transition-all duration-300 animate-fade-in">
      <div className="flex items-start justify-between mb-2">
        <div className="p-2 rounded-lg bg-primary/10">
          {icon}
        </div>
        {trend && (
          <Badge variant="outline" className="bg-success/10 text-success border-success/20 text-xs">
            <TrendingUp className="h-3 w-3 mr-1" />
            {trend === "up" ? "+12%" : "Stable"}
          </Badge>
        )}
      </div>
      <div className="space-y-1">
        <p className="text-xs text-muted-foreground font-medium">{label}</p>
        <p className="text-2xl font-bold text-foreground">{value}</p>
        {subtext && (
          <p className="text-xs text-muted-foreground">{subtext}</p>
        )}
      </div>
    </Card>
  );
};

export const LiveMetricsGrid = () => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <MetricCard
        icon={<Zap className="h-5 w-5 text-warning" />}
        label="Search Time"
        value="142 ms"
        subtext="Avg. hybrid query latency"
        trend="stable"
      />
      <MetricCard
        icon={<Activity className="h-5 w-5 text-success" />}
        label="Success Match Rate"
        value="89%"
        subtext="Application-dog compatibility"
        trend="up"
      />
      <MetricCard
        icon={<Globe className="h-5 w-5 text-primary" />}
        label="Translation API"
        value="Korean → English"
        subtext="Real-time multilingual support"
      />
      <MetricCard
        icon={<Zap className="h-5 w-5 text-secondary" />}
        label="Active Embeddings"
        value="1,247"
        subtext="768-dim vector space"
      />
    </div>
  );
};
