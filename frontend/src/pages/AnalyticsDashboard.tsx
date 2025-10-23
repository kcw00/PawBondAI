import { ArrowLeft, TrendingUp, Target, Zap, Database } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useNavigate } from "react-router-dom";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

export default function AnalyticsDashboard() {
  const navigate = useNavigate();

  // Mock data for charts
  const queryPerformanceData = [
    { month: "Oct", semantic: 145, structured: 98, hybrid: 187 },
    { month: "Nov", semantic: 156, structured: 105, hybrid: 198 },
    { month: "Dec", semantic: 168, structured: 112, hybrid: 210 },
    { month: "Jan", semantic: 182, structured: 118, hybrid: 225 },
    { month: "Feb", semantic: 195, structured: 125, hybrid: 238 },
    { month: "Mar", semantic: 210, structured: 132, hybrid: 252 },
  ];

  const adoptionSuccessData = [
    { month: "Oct", successful: 42, returned: 3, pending: 12 },
    { month: "Nov", successful: 48, returned: 2, pending: 15 },
    { month: "Dec", successful: 55, returned: 4, pending: 18 },
    { month: "Jan", successful: 61, returned: 3, pending: 20 },
    { month: "Feb", successful: 68, returned: 2, pending: 22 },
    { month: "Mar", successful: 75, returned: 3, pending: 25 },
  ];

  const vectorSimilarityData = [
    { range: "0.9-1.0", count: 45, label: "Perfect Match" },
    { range: "0.8-0.9", count: 98, label: "Excellent" },
    { range: "0.7-0.8", count: 142, label: "Good" },
    { range: "0.6-0.7", count: 87, label: "Fair" },
    { range: "0.5-0.6", count: 34, label: "Poor" },
  ];

  const rrfWeightingData = [
    { name: "Semantic 70%", value: 70 },
    { name: "Structured 30%", value: 30 },
  ];

  const latencyTrendData = [
    { week: "W1", semantic: 125, structured: 45, rrf: 15 },
    { week: "W2", semantic: 132, structured: 48, rrf: 16 },
    { week: "W3", semantic: 128, structured: 42, rrf: 14 },
    { week: "W4", semantic: 135, structured: 50, rrf: 17 },
    { week: "W5", semantic: 130, structured: 46, rrf: 15 },
    { week: "W6", semantic: 142, structured: 52, rrf: 18 },
  ];

  const COLORS = {
    semantic: "#00BFB3", // Elastic teal
    structured: "#F04E98", // Elastic pink
    hybrid: "#7B61FF", // Elastic purple
    success: "#54B399", // Elastic green
    warning: "#FEC514", // Elastic yellow
    neutral: "#98A2B3", // Elastic gray
  };

  return (
    <div className="flex flex-col h-screen bg-background overflow-hidden">
      {/* Header */}
      <div className="bg-card px-6 py-4 flex-shrink-0 border-b border-border">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => navigate("/")}
              className="hover:bg-muted/50"
            >
              <ArrowLeft className="h-4 w-4" />
            </Button>
            <div>
              <h1 className="text-lg font-bold text-foreground mb-0.5">
                Elastic AI Search Analytics
              </h1>
              <p className="text-xs text-muted-foreground">
                Hybrid query performance & adoption insights
              </p>
            </div>
          </div>
          <Badge variant="outline" className="bg-success/10 text-success border-success/20">
            Live Data
          </Badge>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-7xl mx-auto px-6 py-6 space-y-6">
          {/* KPI Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="p-4 border-l-4 border-l-[#00BFB3]">
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs text-muted-foreground font-medium">Avg Query Time</p>
                <Zap className="h-4 w-4 text-[#00BFB3]" />
              </div>
              <p className="text-2xl font-bold text-foreground">142ms</p>
              <p className="text-xs text-success mt-1">↓ 8% vs last month</p>
            </Card>

            <Card className="p-4 border-l-4 border-l-[#7B61FF]">
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs text-muted-foreground font-medium">Match Success Rate</p>
                <Target className="h-4 w-4 text-[#7B61FF]" />
              </div>
              <p className="text-2xl font-bold text-foreground">89%</p>
              <p className="text-xs text-success mt-1">↑ 5% vs last month</p>
            </Card>

            <Card className="p-4 border-l-4 border-l-[#54B399]">
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs text-muted-foreground font-medium">Adoptions (30d)</p>
                <TrendingUp className="h-4 w-4 text-[#54B399]" />
              </div>
              <p className="text-2xl font-bold text-foreground">75</p>
              <p className="text-xs text-success mt-1">↑ 10% vs last month</p>
            </Card>

            <Card className="p-4 border-l-4 border-l-[#F04E98]">
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs text-muted-foreground font-medium">Vector Embeddings</p>
                <Database className="h-4 w-4 text-[#F04E98]" />
              </div>
              <p className="text-2xl font-bold text-foreground">1,247</p>
              <p className="text-xs text-muted-foreground mt-1">768-dim vectors</p>
            </Card>
          </div>

          {/* Query Performance Trends */}
          <Card className="p-6">
            <div className="mb-4">
              <h3 className="text-base font-semibold text-foreground mb-1">
                Query Performance by Method
              </h3>
              <p className="text-xs text-muted-foreground">
                Average query latency (ms) across search methods
              </p>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={queryPerformanceData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} label={{ value: 'Latency (ms)', angle: -90, position: 'insideLeft', style: { fontSize: 12 } }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#fff",
                    border: "1px solid #E5E7EB",
                    borderRadius: "8px",
                    fontSize: "12px",
                  }}
                />
                <Legend wrapperStyle={{ fontSize: "12px" }} />
                <Line
                  type="monotone"
                  dataKey="semantic"
                  stroke={COLORS.semantic}
                  strokeWidth={2}
                  name="Semantic Only"
                  dot={{ r: 4 }}
                />
                <Line
                  type="monotone"
                  dataKey="structured"
                  stroke={COLORS.structured}
                  strokeWidth={2}
                  name="Structured Only"
                  dot={{ r: 4 }}
                />
                <Line
                  type="monotone"
                  dataKey="hybrid"
                  stroke={COLORS.hybrid}
                  strokeWidth={2}
                  name="Hybrid (RRF)"
                  dot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </Card>

          {/* Two Column Layout */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Adoption Success Patterns */}
            <Card className="p-6">
              <div className="mb-4">
                <h3 className="text-base font-semibold text-foreground mb-1">
                  Adoption Success Patterns
                </h3>
                <p className="text-xs text-muted-foreground">
                  Monthly adoption outcomes tracked
                </p>
              </div>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={adoptionSuccessData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                  <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#fff",
                      border: "1px solid #E5E7EB",
                      borderRadius: "8px",
                      fontSize: "12px",
                    }}
                  />
                  <Legend wrapperStyle={{ fontSize: "12px" }} />
                  <Area
                    type="monotone"
                    dataKey="successful"
                    stackId="1"
                    stroke={COLORS.success}
                    fill={COLORS.success}
                    fillOpacity={0.6}
                    name="Successful"
                  />
                  <Area
                    type="monotone"
                    dataKey="pending"
                    stackId="1"
                    stroke={COLORS.warning}
                    fill={COLORS.warning}
                    fillOpacity={0.6}
                    name="Pending"
                  />
                  <Area
                    type="monotone"
                    dataKey="returned"
                    stackId="1"
                    stroke={COLORS.structured}
                    fill={COLORS.structured}
                    fillOpacity={0.6}
                    name="Returned"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </Card>

            {/* Vector Similarity Distribution */}
            <Card className="p-6">
              <div className="mb-4">
                <h3 className="text-base font-semibold text-foreground mb-1">
                  Vector Similarity Distribution
                </h3>
                <p className="text-xs text-muted-foreground">
                  Cosine similarity scores (0-1 scale)
                </p>
              </div>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={vectorSimilarityData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                  <XAxis dataKey="range" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 12 }} label={{ value: 'Document Count', angle: -90, position: 'insideLeft', style: { fontSize: 12 } }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#fff",
                      border: "1px solid #E5E7EB",
                      borderRadius: "8px",
                      fontSize: "12px",
                    }}
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        return (
                          <div className="bg-white border border-border rounded-lg p-3 shadow-lg">
                            <p className="text-xs font-semibold mb-1">{payload[0].payload.label}</p>
                            <p className="text-xs text-muted-foreground">
                              Similarity: {payload[0].payload.range}
                            </p>
                            <p className="text-xs font-medium">
                              Count: {payload[0].value}
                            </p>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <Bar dataKey="count" fill={COLORS.semantic} radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </Card>
          </div>

          {/* Bottom Row */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* RRF Weighting */}
            <Card className="p-6">
              <div className="mb-4">
                <h3 className="text-base font-semibold text-foreground mb-1">
                  RRF Weighting Strategy
                </h3>
                <p className="text-xs text-muted-foreground">
                  Current hybrid search configuration
                </p>
              </div>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie
                    data={rrfWeightingData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value }) => `${name}: ${value}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    <Cell fill={COLORS.semantic} />
                    <Cell fill={COLORS.structured} />
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#fff",
                      border: "1px solid #E5E7EB",
                      borderRadius: "8px",
                      fontSize: "12px",
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </Card>

            {/* Latency Breakdown */}
            <Card className="p-6 md:col-span-2">
              <div className="mb-4">
                <h3 className="text-base font-semibold text-foreground mb-1">
                  Query Latency Breakdown
                </h3>
                <p className="text-xs text-muted-foreground">
                  Average processing time per stage (ms)
                </p>
              </div>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={latencyTrendData} layout="horizontal">
                  <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                  <XAxis type="category" dataKey="week" tick={{ fontSize: 12 }} />
                  <YAxis type="number" tick={{ fontSize: 12 }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#fff",
                      border: "1px solid #E5E7EB",
                      borderRadius: "8px",
                      fontSize: "12px",
                    }}
                  />
                  <Legend wrapperStyle={{ fontSize: "12px" }} />
                  <Bar dataKey="semantic" stackId="a" fill={COLORS.semantic} name="Semantic Search" />
                  <Bar dataKey="structured" stackId="a" fill={COLORS.structured} name="Structured Filter" />
                  <Bar dataKey="rrf" stackId="a" fill={COLORS.hybrid} name="RRF Fusion" />
                </BarChart>
              </ResponsiveContainer>
            </Card>
          </div>

          {/* Technical Metrics */}
          <Card className="p-6">
            <h3 className="text-base font-semibold text-foreground mb-4">
              Technical Performance Metrics
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-muted/30 rounded p-3">
                <p className="text-xs text-muted-foreground mb-1">Index Size</p>
                <p className="text-lg font-semibold text-foreground">2.4 GB</p>
                <p className="text-xs text-muted-foreground mt-1">419 documents</p>
              </div>
              <div className="bg-muted/30 rounded p-3">
                <p className="text-xs text-muted-foreground mb-1">Avg kNN Candidates</p>
                <p className="text-lg font-semibold text-foreground">200</p>
                <p className="text-xs text-muted-foreground mt-1">per query</p>
              </div>
              <div className="bg-muted/30 rounded p-3">
                <p className="text-xs text-muted-foreground mb-1">Cache Hit Rate</p>
                <p className="text-lg font-semibold text-foreground">76%</p>
                <p className="text-xs text-success mt-1">↑ 3% vs last week</p>
              </div>
              <div className="bg-muted/30 rounded p-3">
                <p className="text-xs text-muted-foreground mb-1">RRF Rank Window</p>
                <p className="text-lg font-semibold text-foreground">50</p>
                <p className="text-xs text-muted-foreground mt-1">top results combined</p>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
