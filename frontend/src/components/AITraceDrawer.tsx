import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2, Brain, Search, Zap, ChevronRight } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";

interface TraceStep {
  id: string;
  label: string;
  status: "complete" | "processing" | "pending";
  duration?: number;
  details?: string;
  data?: any;
}

interface AITraceDrawerProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  searchType?: 'behavioral' | 'multiCriteria' | 'similarity' | 'behavioralAnalysis';
  query?: string;
}

export const AITraceDrawer = ({ open, onOpenChange, searchType, query }: AITraceDrawerProps) => {
  // Mock trace data based on search type
  const getTraceSteps = (): TraceStep[] => {
    if (!searchType) return [];

    const baseSteps: TraceStep[] = [
      {
        id: "intent",
        label: "Gemini Intent Detection",
        status: "complete",
        duration: 145,
        details: "text-embedding-005",
        data: {
          detected_intent: searchType === 'behavioral' ? "adopter_matching" : 
                          searchType === 'multiCriteria' ? "multi_criteria_search" :
                          searchType === 'similarity' ? "similarity_search" : "behavioral_analysis",
          confidence: 0.94,
          entities: searchType === 'behavioral' ? ["separation anxiety", "experience"] : 
                   searchType === 'multiCriteria' ? ["work from home", "yard", "senior"] : 
                   searchType === 'similarity' ? ["Emily Rodriguez"] : ["foster report", "Luna"]
        }
      }
    ];

    if (searchType === 'behavioral') {
      baseSteps.push(
        {
          id: "embedding",
          label: "Generate Query Embeddings",
          status: "complete",
          duration: 89,
          details: "VertexAI text-embedding-004",
          data: {
            dimensions: 768,
            query_vector: "[0.023, -0.145, 0.891, ...]"
          }
        },
        {
          id: "elastic-semantic",
          label: "Elasticsearch Semantic Search",
          status: "complete",
          duration: 142,
          data: {
            index: "adopters",
            query_type: "knn",
            k: 50,
            num_candidates: 200,
            vector_field: "application_embedding"
          }
        },
        {
          id: "elastic-structured",
          label: "Elasticsearch Structured Filters",
          status: "complete",
          duration: 38,
          data: {
            filters: [
              "previous_experience: 'anxious dogs'",
              "employment_status: 'remote' OR 'retired'"
            ]
          }
        },
        {
          id: "rrf",
          label: "RRF Rank Fusion",
          status: "complete",
          duration: 12,
          data: {
            semantic_weight: 0.70,
            structured_weight: 0.30,
            final_results: 5
          }
        }
      );
    } else if (searchType === 'multiCriteria') {
      baseSteps.push(
        {
          id: "embedding",
          label: "Generate Query Embeddings",
          status: "complete",
          duration: 92,
          details: "VertexAI text-embedding-004",
          data: {
            dimensions: 768,
            query_parts: ["experienced senior dogs", "medical needs"]
          }
        },
        {
          id: "elastic-hybrid",
          label: "Elasticsearch Hybrid Query",
          status: "complete",
          duration: 156,
          data: {
            semantic_match: "experienced medical needs senior",
            structured_filters: [
              "employment_status = 'remote'",
              "housing_type = 'house'",
              "has_yard = true",
              "senior_experience = true"
            ]
          }
        },
        {
          id: "rrf",
          label: "RRF Rank Fusion",
          status: "complete",
          duration: 15,
          data: {
            semantic_weight: 0.65,
            structured_weight: 0.35,
            final_results: 3
          }
        }
      );
    } else if (searchType === 'similarity') {
      baseSteps.push(
        {
          id: "profile-fetch",
          label: "Fetch Reference Profile",
          status: "complete",
          duration: 34,
          data: {
            adopter_id: "emily_rodriguez",
            embedding_cached: true
          }
        },
        {
          id: "elastic-vector",
          label: "Elasticsearch Vector Search",
          status: "complete",
          duration: 128,
          data: {
            query_type: "knn",
            k: 5,
            similarity: "cosine",
            min_score: 0.85
          }
        },
        {
          id: "filter-outcomes",
          label: "Filter by Success Outcomes",
          status: "complete",
          duration: 22,
          data: {
            filter: "adoption_outcome = 'successful'",
            matched: 5
          }
        }
      );
    } else if (searchType === 'behavioralAnalysis') {
      baseSteps.push(
        {
          id: "extract-patterns",
          label: "Extract Behavioral Patterns",
          status: "complete",
          duration: 234,
          details: "Gemini 2.5 Flash",
          data: {
            patterns_found: 5,
            progress_indicators: ["reduced hiding", "tail wagging", "approaching"],
            concerns: ["loud noises", "doorbell"]
          }
        },
        {
          id: "embedding",
          label: "Generate Report Embeddings",
          status: "complete",
          duration: 98,
          details: "VertexAI text-embedding-004",
          data: {
            dimensions: 768
          }
        },
        {
          id: "elastic-similar",
          label: "Find Similar Foster Cases",
          status: "complete",
          duration: 167,
          data: {
            index: "foster_reports",
            similar_cases: 8,
            avg_similarity: 0.87
          }
        },
        {
          id: "analyze-timeline",
          label: "Analyze Progress Timeline",
          status: "complete",
          duration: 89,
          data: {
            current_week: 3,
            predicted_adoption_ready: "5-7 weeks",
            confidence: 0.89
          }
        }
      );
    }

    return baseSteps;
  };

  const steps = getTraceSteps();
  const totalDuration = steps.reduce((sum, step) => sum + (step.duration || 0), 0);

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="right" className="w-[500px] sm:w-[600px] p-0">
        <SheetHeader className="px-6 py-4 border-b border-border bg-muted/30">
          <div className="flex items-center justify-between">
            <SheetTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5 text-primary" />
              AI Trace
            </SheetTitle>
            {steps.length > 0 && (
              <Badge variant="outline" className="font-mono text-xs">
                {totalDuration}ms
              </Badge>
            )}
          </div>
          {query && (
            <p className="text-sm text-muted-foreground mt-2 font-mono">
              "{query}"
            </p>
          )}
        </SheetHeader>

        <ScrollArea className="h-[calc(100vh-100px)]">
          <div className="p-6 space-y-4">
            {steps.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <Search className="h-12 w-12 text-muted-foreground mb-3" />
                <p className="text-sm text-muted-foreground">
                  No trace data available.<br />
                  Execute a search query to see the AI reasoning chain.
                </p>
              </div>
            ) : (
              steps.map((step, index) => (
                <div key={step.id} className="relative">
                  {/* Connection line */}
                  {index < steps.length - 1 && (
                    <div className="absolute left-[11px] top-[32px] w-[2px] h-[calc(100%+16px)] bg-border" />
                  )}

                  {/* Step card */}
                  <div className="relative bg-card border border-border rounded-lg p-4 hover:border-primary/50 transition-colors">
                    <div className="flex items-start gap-3">
                      {/* Status icon */}
                      <div className="flex-shrink-0 mt-0.5">
                        {step.status === "complete" ? (
                          <CheckCircle2 className="h-5 w-5 text-success" />
                        ) : step.status === "processing" ? (
                          <Zap className="h-5 w-5 text-warning animate-pulse" />
                        ) : (
                          <div className="h-5 w-5 rounded-full border-2 border-muted" />
                        )}
                      </div>

                      {/* Content */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between gap-2 mb-1">
                          <h4 className="text-sm font-semibold text-foreground">
                            {step.label}
                          </h4>
                          {step.duration && (
                            <Badge variant="secondary" className="font-mono text-xs">
                              {step.duration}ms
                            </Badge>
                          )}
                        </div>

                        {step.details && (
                          <p className="text-xs text-muted-foreground mb-2 font-mono">
                            {step.details}
                          </p>
                        )}

                        {/* Data details */}
                        {step.data && (
                          <div className="mt-3 bg-muted/50 rounded p-3 text-xs font-mono space-y-1">
                            {Object.entries(step.data).map(([key, value]) => (
                              <div key={key} className="flex items-start gap-2">
                                <ChevronRight className="h-3 w-3 text-muted-foreground flex-shrink-0 mt-0.5" />
                                <div className="flex-1 min-w-0">
                                  <span className="text-muted-foreground">{key}:</span>{" "}
                                  <span className="text-foreground break-all">
                                    {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                                  </span>
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}

            {/* Summary */}
            {steps.length > 0 && (
              <div className="mt-6 p-4 bg-success/10 border border-success/20 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <CheckCircle2 className="h-4 w-4 text-success" />
                  <h4 className="text-sm font-semibold text-success">Query Complete</h4>
                </div>
                <p className="text-xs text-muted-foreground font-mono">
                  Processed {steps.length} steps in {totalDuration}ms
                </p>
              </div>
            )}
          </div>
        </ScrollArea>
      </SheetContent>
    </Sheet>
  );
};
