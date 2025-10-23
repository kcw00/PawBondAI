import { CheckCircle2, Upload, FileText, Languages, Sparkles, Database } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface PipelineStepsProps {
  currentStep?: number; // 0 = none, 1-5 = active step
  showModels?: boolean;
}

export const PipelineSteps = ({ currentStep = 5, showModels = true }: PipelineStepsProps) => {
  const steps = [
    {
      id: 1,
      label: "Upload",
      icon: Upload,
      model: "Local",
      color: "text-primary"
    },
    {
      id: 2,
      label: "OCR",
      icon: FileText,
      model: "Vision AI",
      color: "text-primary"
    },
    {
      id: 3,
      label: "Translation",
      icon: Languages,
      model: "Vertex Translation API",
      color: "text-primary"
    },
    {
      id: 4,
      label: "Embedding",
      icon: Sparkles,
      model: "google_vertex_ai_embedding",
      color: "text-primary"
    },
    {
      id: 5,
      label: "Indexed",
      icon: Database,
      model: "Elasticsearch",
      color: "text-success"
    }
  ];

  const isStepComplete = (stepId: number) => currentStep >= stepId;
  const isStepActive = (stepId: number) => currentStep === stepId;

  return (
    <div className="relative">
      {/* Steps container */}
      <div className="flex items-center justify-between relative">
        {/* Connection line */}
        <div className="absolute top-5 left-0 right-0 h-[2px] bg-border" 
             style={{ 
               marginLeft: '20px', 
               marginRight: '20px',
               width: 'calc(100% - 40px)' 
             }} 
        />
        
        {/* Progress line */}
        <div 
          className="absolute top-5 left-0 h-[2px] bg-success transition-all duration-500" 
          style={{ 
            marginLeft: '20px',
            width: `calc(${((currentStep - 1) / (steps.length - 1)) * 100}% - ${40 / steps.length}px)`
          }} 
        />

        {/* Step items */}
        {steps.map((step, index) => {
          const StepIcon = step.icon;
          const complete = isStepComplete(step.id);
          const active = isStepActive(step.id);

          return (
            <div key={step.id} className="flex-1 flex flex-col items-center relative z-10">
              {/* Circle */}
              <div 
                className={`w-10 h-10 rounded-full flex items-center justify-center transition-all duration-300 ${
                  complete 
                    ? 'bg-success text-white' 
                    : active 
                    ? 'bg-primary/20 text-primary border-2 border-primary animate-pulse' 
                    : 'bg-muted text-muted-foreground'
                }`}
              >
                {complete && !active ? (
                  <CheckCircle2 className="h-5 w-5" />
                ) : (
                  <StepIcon className="h-5 w-5" />
                )}
              </div>

              {/* Label */}
              <div className="mt-2 text-center min-h-[40px]">
                <p className={`text-xs font-semibold ${
                  complete ? 'text-foreground' : 'text-muted-foreground'
                }`}>
                  {step.label}
                </p>
                {showModels && (
                  <p className={`text-[10px] mt-1 font-mono ${
                    complete ? 'text-muted-foreground' : 'text-muted-foreground/60'
                  }`}>
                    {step.model}
                  </p>
                )}
              </div>

              {/* Active indicator */}
              {active && currentStep < steps.length && (
                <Badge variant="secondary" className="mt-1 text-[10px] px-1.5 py-0 h-4 animate-pulse">
                  Processing
                </Badge>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
