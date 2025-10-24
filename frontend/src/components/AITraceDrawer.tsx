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

interface TraceData {
  steps: TraceStep[];
  total_duration_ms: number;
  query: string;
}

interface AITraceDrawerProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  traceData?: TraceData | null;
}

export const AITraceDrawer = ({ open, onOpenChange, traceData }: AITraceDrawerProps) => {
  // Use real trace data from backend
  const steps = traceData?.steps || [];
  const totalDuration = traceData?.total_duration_ms || 0;
  const query = traceData?.query || "";

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
