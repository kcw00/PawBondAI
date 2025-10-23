import { useState, useRef } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { FileText, Dog, BookOpen, Upload, ArrowLeft, Sparkles } from "lucide-react";
import { IndexStatusWidget } from "@/components/data-management/IndexStatusWidget";
import { UploadModal } from "@/components/data-management/UploadModal";
import { PipelineSteps } from "@/components/data-management/PipelineSteps";
import { EmbeddingPreviewModal } from "@/components/data-management/EmbeddingPreviewModal";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";

export default function DataManagementPage() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'applications' | 'dogs' | 'cases'>('applications');
  const [showEmbeddingPreview, setShowEmbeddingPreview] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<{
    isUploading: boolean;
    fileName: string;
    totalRows: number;
    currentRow: number;
    stage: 'uploading' | 'parsing' | 'extracting' | 'embedding' | 'indexing' | 'complete';
  } | null>(null);

  const applicationsInputRef = useRef<HTMLInputElement>(null);
  const dogsInputRef = useRef<HTMLInputElement>(null);
  const casesInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = (type: 'applications' | 'dogs' | 'cases') => async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Set initial upload state
    setUploadProgress({
      isUploading: true,
      fileName: file.name,
      totalRows: 0,
      currentRow: 0,
      stage: 'uploading'
    });

    try {
      const formData = new FormData();
      formData.append('file', file);

      // Different endpoints for different types
      const uploadEndpoint = type === 'applications'
        ? '/api/v1/applications/csv/upload'
        : type === 'dogs'
        ? '/api/v1/dogs/bulk-upload'
        : '/api/v1/outcomes/csv/upload'; // cases endpoint

      setUploadProgress(prev => prev ? { ...prev, stage: 'parsing' } : null);

      const response = await fetch(`http://localhost:8000${uploadEndpoint}`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      const data = await response.json();

      // Update progress through stages
      setUploadProgress(prev => prev ? {
        ...prev,
        stage: 'extracting',
        totalRows: data.total_processed || data.total_rows || 0
      } : null);

      setTimeout(() => {
        setUploadProgress(prev => prev ? { ...prev, stage: 'embedding' } : null);
      }, 500);

      setTimeout(() => {
        setUploadProgress(prev => prev ? {
          ...prev,
          stage: 'indexing',
          currentRow: data.indexed_count || data.successful || 0
        } : null);
      }, 1000);

      setTimeout(() => {
        setUploadProgress(prev => prev ? { ...prev, stage: 'complete' } : null);

        toast.success(`Successfully indexed ${data.indexed_count || data.successful || 0} ${type}!`);

        if (data.failed_count > 0 || data.failed > 0) {
          toast.warning(`${data.failed_count || data.failed} rows failed to index`);
        }
      }, 1500);

    } catch (error) {
      console.error('Upload error:', error);
      toast.error(`Upload failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
      setUploadProgress(null);
    }
  };

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      {uploadProgress && (
        <UploadModal
          fileName={uploadProgress.fileName}
          totalRows={uploadProgress.totalRows}
          currentRow={uploadProgress.currentRow}
          stage={uploadProgress.stage}
          onClose={() => setUploadProgress(null)}
        />
      )}

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <div className="bg-card px-6 py-4 flex-shrink-0 border-b border-border">
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
              <h1 className="text-lg font-bold text-foreground mb-0.5">Data Management</h1>
              <p className="text-xs text-muted-foreground">Upload and manage your indexed data</p>
            </div>
          </div>
        </div>

        {/* Navigation Bar */}
        <div className="bg-background px-6 flex-shrink-0 border-b border-border overflow-x-auto">
          <div className="flex gap-8 min-w-max justify-center">
            <button
              className={`py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${activeTab === 'applications'
                ? 'border-primary text-foreground'
                : 'border-transparent text-muted-foreground hover:text-foreground'
                }`}
              onClick={() => {
                setActiveTab('applications');
                const element = document.getElementById('applications-section');
                element?.scrollIntoView({ behavior: 'smooth' });
              }}
            >
              Applications
            </button>
            <button
              className={`py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${activeTab === 'dogs'
                ? 'border-primary text-foreground'
                : 'border-transparent text-muted-foreground hover:text-foreground'
                }`}
              onClick={() => {
                setActiveTab('dogs');
                const element = document.getElementById('dogs-section');
                element?.scrollIntoView({ behavior: 'smooth' });
              }}
            >
              Dogs
            </button>
            <button
              className={`py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${activeTab === 'cases'
                ? 'border-primary text-foreground'
                : 'border-transparent text-muted-foreground hover:text-foreground'
                }`}
              onClick={() => {
                setActiveTab('cases');
                const element = document.getElementById('cases-section');
                element?.scrollIntoView({ behavior: 'smooth' });
              }}
            >
              Success Cases
            </button>
          </div>
        </div>

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto">
          <div className="max-w-5xl mx-auto px-6 py-6 space-y-6">
            {/* Card 1: Adoption Applications */}
            <Card id="applications-section" className="p-6 bg-card border-border scroll-mt-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <FileText className="h-6 w-6 text-[#718355]" />
                  <div>
                    <h2 className="text-xl font-bold text-foreground">📋 Adoption Applications</h2>
                    <p className="text-sm text-muted-foreground">Primary data source for semantic search</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="secondary" className="bg-[#6a994e]/20 text-[#6a994e]">
                    ✅ 203 indexed
                  </Badge>
                  <Button
                    variant="outline"
                    size="sm"
                    className="gap-1 text-xs h-7"
                    onClick={() => setShowEmbeddingPreview(true)}
                  >
                    <Sparkles className="h-3 w-3" />
                    Vector preview
                  </Button>
                </div>
              </div>

              {/* Pipeline Visualization */}
              <div className="mb-6 p-4 bg-muted/30 rounded-lg border border-border">
                <div className="mb-3 flex items-center justify-between">
                  <p className="text-xs font-semibold text-foreground">Elastic–Vertex AI Indexing Pipeline</p>
                  <Badge variant="outline" className="text-[10px] px-1.5 h-5 bg-success/10 text-success border-success/30">
                    All stages complete
                  </Badge>
                </div>
                <PipelineSteps currentStep={5} showModels={true} />
              </div>

              <div className="space-y-4">
                <div
                  className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-[#718355] hover:bg-[#718355]/5 transition-colors cursor-pointer"
                  onClick={() => applicationsInputRef.current?.click()}
                >
                  <Upload className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                  <p className="text-sm font-medium text-foreground mb-1">Drop CSV/Excel/PDF files here</p>
                  <p className="text-xs text-muted-foreground mb-3">or click to browse</p>
                  <Button variant="outline" size="sm">Browse Files</Button>
                  <input
                    ref={applicationsInputRef}
                    type="file"
                    accept=".csv,.xlsx,.xls,.pdf,.txt"
                    className="hidden"
                    onChange={handleFileUpload('applications')}
                  />
                </div>

                <div className="bg-muted/30 p-4 rounded-lg space-y-3">
                  <div>
                    <p className="text-sm font-semibold text-foreground mb-2">Accepted formats:</p>
                    <div className="text-xs text-muted-foreground space-y-1">
                      <p>• CSV/Excel (.csv, .xlsx) - bulk import</p>
                      <p>• PDF (.pdf) - individual applications</p>
                      <p>• Text (.txt) - application text</p>
                    </div>
                  </div>

                  <div>
                    <p className="text-sm font-semibold text-foreground mb-2">What we extract:</p>
                    <div className="text-xs text-muted-foreground space-y-1">
                      <p>• Applicant motivation (semantic search)</p>
                      <p>• Experience level (structured field)</p>
                      <p>• Housing information (structured)</p>
                      <p>• Work schedule (structured)</p>
                      <p>• Previous dog experience (semantic)</p>
                    </div>
                  </div>

                  <div>
                    <p className="text-sm font-semibold text-foreground mb-2">Processing pipeline:</p>
                    <div className="text-xs text-muted-foreground space-y-1">
                      <p>1. Extract text from documents</p>
                      <p>2. Generate 768-dim embeddings</p>
                      <p>3. Index to Elasticsearch</p>
                      <p>4. Ready for semantic search ✓</p>
                    </div>
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button variant="outline" size="sm" className="flex-1">
                    Download Template
                  </Button>
                  <Button variant="outline" size="sm" className="flex-1">
                    View Indexed Data
                  </Button>
                </div>

                <div className="border-t pt-4">
                  <p className="text-xs font-semibold text-foreground mb-2">Recent uploads:</p>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-xs">
                      <div>
                        <p className="font-medium text-foreground">applications_oct2024.csv (203 rows)</p>
                        <p className="text-muted-foreground">Uploaded: Oct 15, 10:30 AM</p>
                      </div>
                      <Badge variant="secondary" className="bg-[#6a994e]/20 text-[#6a994e]">✓</Badge>
                    </div>
                  </div>
                </div>
              </div>
            </Card>

            {/* Card 2: Dog Profiles */}
            <Card id="dogs-section" className="p-6 bg-card border-border scroll-mt-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <Dog className="h-6 w-6 text-[#718355]" />
                  <div>
                    <h2 className="text-xl font-bold text-foreground">🐕 Dog Profiles</h2>
                    <p className="text-sm text-muted-foreground">Available dogs for adoption</p>
                  </div>
                </div>
                <Badge variant="secondary" className="bg-[#6a994e]/20 text-[#6a994e]">
                  ✅ 127 indexed
                </Badge>
              </div>

              <div className="space-y-4">
                <div
                  className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-[#718355] hover:bg-[#718355]/5 transition-colors cursor-pointer"
                  onClick={() => dogsInputRef.current?.click()}
                >
                  <Upload className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                  <p className="text-sm font-medium text-foreground mb-1">Drop files here or click to browse</p>
                  <Button variant="outline" size="sm" className="mt-2">Browse Files</Button>
                  <input
                    ref={dogsInputRef}
                    type="file"
                    accept=".csv,.xlsx,.xls,.json"
                    className="hidden"
                    onChange={handleFileUpload('dogs')}
                  />
                </div>

                <div className="bg-muted/30 p-4 rounded-lg space-y-2">
                  <p className="text-sm font-semibold text-foreground mb-2">What we index:</p>
                  <div className="text-xs text-muted-foreground space-y-1">
                    <p>• Name, age, breed</p>
                    <p>• Personality traits (for semantic)</p>
                    <p>• Behavioral notes (for semantic)</p>
                    <p>• Medical needs (structured)</p>
                    <p>• Current status (structured)</p>
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button variant="outline" size="sm" className="flex-1">
                    Upload
                  </Button>
                  <Button variant="outline" size="sm" className="flex-1">
                    View Dogs
                  </Button>
                </div>
              </div>
            </Card>

            {/* Card 3: Adoption Success Cases */}
            <Card id="cases-section" className="p-6 bg-card border-border scroll-mt-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <BookOpen className="h-6 w-6 text-[#718355]" />
                  <div>
                    <h2 className="text-xl font-bold text-foreground">📚 Adoption Success Cases</h2>
                    <p className="text-sm text-muted-foreground">Historical outcomes for pattern learning</p>
                  </div>
                </div>
                <Badge variant="secondary" className="bg-[#6a994e]/20 text-[#6a994e]">
                  ✅ 89 indexed
                </Badge>
              </div>

              <div className="space-y-4">
                <div className="bg-[#CFE1B9]/20 p-4 rounded-lg">
                  <p className="text-sm font-semibold text-foreground mb-2">Why this matters:</p>
                  <p className="text-xs text-muted-foreground">
                    AI learns from these outcomes to predict future success. The more data, the smarter the matching becomes.
                  </p>
                </div>

                <div
                  className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-[#718355] hover:bg-[#718355]/5 transition-colors cursor-pointer"
                  onClick={() => casesInputRef.current?.click()}
                >
                  <Upload className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                  <p className="text-sm font-medium text-foreground mb-1">Upload success cases</p>
                  <Button variant="outline" size="sm" className="mt-2">Browse Files</Button>
                  <input
                    ref={casesInputRef}
                    type="file"
                    accept=".csv,.xlsx,.json"
                    className="hidden"
                    onChange={handleFileUpload('cases')}
                  />
                </div>

                <div className="bg-muted/30 p-4 rounded-lg space-y-2">
                  <p className="text-sm font-semibold text-foreground mb-2">Required fields:</p>
                  <div className="text-xs text-muted-foreground space-y-1">
                    <p>• Dog name & profile</p>
                    <p>• Adopter profile</p>
                    <p>• Outcome (successful/returned)</p>
                    <p>• Follow-up notes</p>
                    <p>• What made it work</p>
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button variant="outline" size="sm" className="flex-1">
                    Upload Cases
                  </Button>
                  <Button variant="outline" size="sm" className="flex-1">
                    View Library
                  </Button>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </div>

      {/* Embedding Preview Modal */}
      <EmbeddingPreviewModal
        open={showEmbeddingPreview}
        onOpenChange={setShowEmbeddingPreview}
      />

      {/* Index Status Widget */}
      <IndexStatusWidget />
    </div>
  );
}