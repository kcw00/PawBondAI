import { useState, useRef, useCallback } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Upload, Download, Eye, FolderUp, Image, Sparkles } from "lucide-react";
import { toast } from "sonner";
import { UploadPreviewModal } from "./UploadPreviewModal";
import { UploadProgressModal } from "./UploadProgressModal";
import { PipelineSteps } from "./PipelineSteps";
import { EmbeddingPreviewModal } from "./EmbeddingPreviewModal";

interface RecentUpload {
  name: string;
  rows?: number;
  date: string;
  status: "success" | "error" | "warning";
  note?: string;
}

interface UploadCardProps {
  title: string;
  icon: React.ReactNode;
  emoji: string;
  status: "indexed" | "empty" | "processing";
  count: number;
  lastUpdate: string;
  acceptedFormats: string[];
  requiredFields?: string[];
  optionalFields?: string[];
  processingPipeline?: string[];
  namingConvention?: {
    examples: string[];
    note: string;
  };
  whyItMatters?: string;
  recentUploads?: RecentUpload[];
  processingQueue?: number;
  hasPhotoUpload?: boolean;
  hasFolderUpload?: boolean;
}

export const UploadCard = ({
  title,
  icon,
  emoji,
  status,
  count,
  lastUpdate,
  acceptedFormats,
  requiredFields,
  optionalFields,
  processingPipeline,
  namingConvention,
  whyItMatters,
  recentUploads,
  processingQueue,
  hasPhotoUpload,
  hasFolderUpload
}: UploadCardProps) => {
  const [isDragging, setIsDragging] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [showProgress, setShowProgress] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [showEmbeddingPreview, setShowEmbeddingPreview] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileSelect(files);
    }
  }, []);

  const handleFileSelect = (files: File[]) => {
    // Show preview modal
    toast.success(`Selected ${files.length} file(s) for upload`);
    setShowPreview(true);
  };

  const handleUploadConfirm = () => {
    setShowPreview(false);
    setShowProgress(true);
    
    // Simulate upload progress
    let progress = 0;
    const interval = setInterval(() => {
      progress += Math.random() * 15;
      if (progress >= 100) {
        progress = 100;
        clearInterval(interval);
        setTimeout(() => {
          setShowProgress(false);
          toast.success("Successfully indexed!", {
            description: `${count} documents are now searchable in the chat interface.`
          });
        }, 500);
      }
      setUploadProgress(Math.min(progress, 100));
    }, 300);
  };

  const getStatusBadge = () => {
    switch (status) {
      case "indexed":
        return (
          <Badge className="bg-success/20 text-success border-success/30">
            ✅ {count} {title.toLowerCase()} indexed
          </Badge>
        );
      case "processing":
        return (
          <Badge className="bg-warning/20 text-warning border-warning/30">
            ⏳ Processing...
          </Badge>
        );
      case "empty":
        return (
          <Badge variant="outline" className="bg-muted">
            No data yet
          </Badge>
        );
    }
  };

  return (
    <>
      <Card className="p-5 hover:shadow-lg transition-all duration-300">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center space-x-2">
            <span className="text-2xl">{emoji}</span>
            <div>
              <h3 className="text-lg font-bold text-foreground">{title}</h3>
              <p className="text-xs text-muted-foreground">Last upload: {lastUpdate}</p>
            </div>
          </div>
        </div>

        {/* Status */}
        <div className="mb-4 flex items-center justify-between">
          {getStatusBadge()}
          {status === "indexed" && (
            <Button 
              variant="outline" 
              size="sm" 
              className="gap-1 text-xs h-7"
              onClick={() => setShowEmbeddingPreview(true)}
            >
              <Sparkles className="h-3 w-3" />
              View vector preview
            </Button>
          )}
        </div>

        {/* Pipeline Visualization */}
        {status === "indexed" && (
          <div className="mb-6 p-4 bg-muted/30 rounded-lg border border-border">
            <div className="mb-3 flex items-center justify-between">
              <p className="text-xs font-semibold text-foreground">Elastic–Vertex AI Indexing Pipeline</p>
              <Badge variant="outline" className="text-[10px] px-1.5 h-5">
                All stages complete
              </Badge>
            </div>
            <PipelineSteps currentStep={5} showModels={true} />
          </div>
        )}

        {/* Drop Zone */}
        <div
          onDragEnter={handleDragEnter}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors cursor-pointer ${
            isDragging
              ? "border-primary bg-primary/10"
              : "border-border hover:border-primary/50 hover:bg-muted/50"
          }`}
          onClick={() => fileInputRef.current?.click()}
        >
          <Upload className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
          <p className="text-sm font-medium text-foreground mb-1">
            Drop {title === "Medical Records" && hasFolderUpload ? "files or folder" : "files"} here
          </p>
          <p className="text-xs text-muted-foreground mb-3">or click to browse</p>
          <Button variant="outline" size="sm" onClick={(e) => e.stopPropagation()}>
            Browse Files
          </Button>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            className="hidden"
            onChange={(e) => {
              const files = Array.from(e.target.files || []);
              if (files.length > 0) handleFileSelect(files);
            }}
          />
        </div>

        {/* Accepted Formats */}
        <div className="mt-4 space-y-3">
          <div>
            <p className="text-xs font-semibold text-muted-foreground mb-2">Accepted formats:</p>
            <ul className="space-y-1">
              {acceptedFormats.map((format, idx) => (
                <li key={idx} className="text-xs text-foreground">• {format}</li>
              ))}
            </ul>
          </div>

          {/* Required Fields */}
          {requiredFields && (
            <div>
              <p className="text-xs font-semibold text-muted-foreground mb-2">Required fields:</p>
              <ul className="space-y-1 max-h-32 overflow-y-auto">
                {requiredFields.map((field, idx) => (
                  <li key={idx} className="text-xs text-foreground">• {field}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Optional Fields */}
          {optionalFields && (
            <div>
              <p className="text-xs font-semibold text-muted-foreground mb-2">Optional but recommended:</p>
              <ul className="space-y-1">
                {optionalFields.map((field, idx) => (
                  <li key={idx} className="text-xs text-foreground">• {field}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Processing Pipeline */}
          {processingPipeline && (
            <div>
              <p className="text-xs font-semibold text-muted-foreground mb-2">Processing pipeline:</p>
              <ul className="space-y-1">
                {processingPipeline.map((step, idx) => (
                  <li key={idx} className="text-xs text-foreground">✓ {step}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Naming Convention */}
          {namingConvention && (
            <div>
              <p className="text-xs font-semibold text-muted-foreground mb-2">Naming convention (auto-detect):</p>
              <ul className="space-y-1 mb-1">
                {namingConvention.examples.map((example, idx) => (
                  <li key={idx} className="text-xs text-foreground">• {example}</li>
                ))}
              </ul>
              <p className="text-xs text-muted-foreground italic">→ {namingConvention.note}</p>
            </div>
          )}

          {/* Why It Matters */}
          {whyItMatters && (
            <div className="p-3 bg-primary/5 border border-primary/20 rounded">
              <p className="text-xs font-semibold text-primary mb-1">Why this matters:</p>
              <p className="text-xs text-foreground">{whyItMatters}</p>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="mt-4 flex flex-wrap gap-2">
          <Button variant="outline" size="sm" className="gap-1">
            <Download className="h-3 w-3" />
            Download Template
          </Button>
          <Button variant="outline" size="sm" className="gap-1">
            <Eye className="h-3 w-3" />
            View Indexed Data
          </Button>
          {hasPhotoUpload && (
            <Button variant="outline" size="sm" className="gap-1">
              <Image className="h-3 w-3" />
              Upload Photos
            </Button>
          )}
          {hasFolderUpload && (
            <Button variant="outline" size="sm" className="gap-1">
              <FolderUp className="h-3 w-3" />
              Upload Folder
            </Button>
          )}
        </div>

        {/* Recent Uploads */}
        {recentUploads && recentUploads.length > 0 && (
          <div className="mt-4 pt-4 border-t border-border">
            <p className="text-xs font-semibold text-muted-foreground mb-2">Recent uploads:</p>
            <div className="space-y-2">
              {recentUploads.map((upload, idx) => (
                <div key={idx} className="flex items-start justify-between text-xs">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-foreground font-medium">{upload.name}</span>
                      {upload.rows && (
                        <span className="text-muted-foreground">({upload.rows} rows)</span>
                      )}
                      {upload.status === "success" && <span className="text-success">✓</span>}
                      {upload.note && (
                        <Badge variant="outline" className="text-xs bg-primary/10 text-primary border-primary/30">
                          {upload.note}
                        </Badge>
                      )}
                    </div>
                    <p className="text-muted-foreground mt-1">Uploaded: {upload.date}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Processing Queue */}
        {processingQueue !== undefined && processingQueue > 0 && (
          <div className="mt-4 p-3 bg-warning/5 border border-warning/20 rounded">
            <p className="text-xs text-foreground">
              ⚙️ Processing: {processingQueue} documents in queue
            </p>
          </div>
        )}
      </Card>

      <UploadPreviewModal
        open={showPreview}
        onClose={() => setShowPreview(false)}
        onConfirm={handleUploadConfirm}
        fileName="applications_oct2024.csv"
        fileType={title}
      />

      <UploadProgressModal
        open={showProgress}
        progress={uploadProgress}
        fileName="applications_oct2024.csv"
      />

      <EmbeddingPreviewModal
        open={showEmbeddingPreview}
        onOpenChange={setShowEmbeddingPreview}
      />
    </>
  );
};
