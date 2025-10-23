import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Progress } from "@/components/ui/progress";
import { CheckCircle2, Loader2 } from "lucide-react";

interface UploadProgressModalProps {
  open: boolean;
  progress: number;
  fileName: string;
}

export const UploadProgressModal = ({
  open,
  progress,
  fileName
}: UploadProgressModalProps) => {
  const steps = [
    { label: "File uploaded to cloud storage", complete: progress > 20 },
    { label: "Parsing CSV data", complete: progress > 40 },
    { label: "Indexing to Elasticsearch", complete: progress > 60 },
    { label: "Generating embeddings", complete: progress > 80 }
  ];

  const documentsIndexed = Math.floor((progress / 100) * 203);
  const timeRemaining = Math.max(0, Math.floor((100 - progress) / 6.67));

  return (
    <Dialog open={open}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Uploading {fileName}</DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Progress Bar */}
          <div>
            <Progress value={progress} className="h-3 mb-2" />
            <p className="text-right text-sm font-medium text-foreground">{Math.floor(progress)}%</p>
          </div>

          {/* Steps */}
          <div className="space-y-3">
            {steps.map((step, idx) => (
              <div key={idx} className="flex items-start gap-2">
                {step.complete ? (
                  <CheckCircle2 className="h-5 w-5 text-success mt-0.5" />
                ) : (
                  <Loader2 className="h-5 w-5 text-muted-foreground animate-spin mt-0.5" />
                )}
                <div className="flex-1">
                  <p className="text-sm text-foreground">{step.label}</p>
                  {idx === 2 && !step.complete && progress > 60 && (
                    <p className="text-xs text-muted-foreground mt-1">
                      • {documentsIndexed}/203 documents indexed
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Estimated Time */}
          {progress < 100 && (
            <p className="text-sm text-muted-foreground text-center">
              Estimated time remaining: {timeRemaining} seconds
            </p>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};
