import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { CheckCircle, Loader2 } from "lucide-react";

interface UploadModalProps {
  fileName: string;
  totalRows: number;
  currentRow: number;
  stage: 'uploading' | 'parsing' | 'extracting' | 'embedding' | 'indexing' | 'complete';
  onClose: () => void;
}

export const UploadModal = ({ fileName, totalRows, currentRow, stage, onClose }: UploadModalProps) => {
  const progress = (currentRow / totalRows) * 100;
  
  const stages = [
    { key: 'uploading', label: 'File uploaded', icon: '✓' },
    { key: 'parsing', label: `Parsing CSV (${totalRows} rows)`, icon: '✓' },
    { key: 'extracting', label: 'Extracting application text', icon: '✓' },
    { key: 'embedding', label: 'Generating embeddings...', icon: '⏳' },
    { key: 'indexing', label: 'Indexing to Elasticsearch...', icon: '⏳' },
  ];

  const currentStageIndex = stages.findIndex(s => s.key === stage);
  const estimatedTime = Math.ceil((totalRows - currentRow) * 0.3);

  if (stage === 'complete') {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
        <Card className="p-6 max-w-md w-full bg-white">
          <div className="text-center space-y-4">
            <CheckCircle className="h-16 w-16 text-[#6a994e] mx-auto" />
            <h3 className="text-xl font-bold text-foreground">Successfully Indexed!</h3>
            <p className="text-sm text-muted-foreground">
              {totalRows} new applications added to Elasticsearch
            </p>
            
            <div className="bg-[#fffcf2] p-4 rounded-lg text-left space-y-2">
              <p className="text-sm font-semibold text-foreground">Summary:</p>
              <div className="text-sm text-foreground space-y-1">
                <p>• Total indexed: {203 + totalRows} applications</p>
                <p>• Embeddings generated: {totalRows}</p>
                <p>• Index time: {Math.ceil(totalRows * 0.8)} seconds</p>
                <p>• Ready for search: ✓</p>
              </div>
            </div>

            <p className="text-sm text-muted-foreground">
              You can now search these applications with the AI!
            </p>

            <div className="flex gap-2">
              <Button 
                onClick={onClose}
                variant="outline"
                className="flex-1"
              >
                Upload More
              </Button>
              <Button 
                onClick={() => window.location.href = '/'}
                className="flex-1 bg-[#718355] hover:bg-[#718355]/90 text-white"
              >
                Go to Chat
              </Button>
            </div>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="p-6 max-w-md w-full bg-white">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-foreground">Processing {fileName}</h3>
            <Loader2 className="h-5 w-5 text-[#718355] animate-spin" />
          </div>

          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Progress</span>
              <span className="font-semibold text-foreground">{Math.round(progress)}%</span>
            </div>
            <Progress value={progress} className="h-2" />
          </div>

          <div className="space-y-2">
            {stages.map((s, idx) => {
              const isComplete = idx < currentStageIndex;
              const isCurrent = idx === currentStageIndex;
              
              return (
                <div key={s.key} className="flex items-center gap-2 text-sm">
                  <span className={isComplete ? "text-[#6a994e]" : isCurrent ? "text-[#718355]" : "text-muted-foreground"}>
                    {isComplete ? '✓' : isCurrent ? '⏳' : '○'}
                  </span>
                  <span className={isComplete ? "text-foreground" : isCurrent ? "text-foreground font-medium" : "text-muted-foreground"}>
                    {s.label}
                  </span>
                </div>
              );
            })}
            
            {stage === 'embedding' && (
              <p className="text-xs text-muted-foreground ml-6">
                • Row {currentRow}/{totalRows}: Creating 768-dim vector
              </p>
            )}
          </div>

          <div className="pt-3 border-t">
            <p className="text-sm text-muted-foreground">
              Estimated time: {estimatedTime} seconds
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
};
