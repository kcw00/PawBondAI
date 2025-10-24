import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Sparkles, Database, Layers } from "lucide-react";

interface EmbeddingPreviewModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export const EmbeddingPreviewModal = ({ open, onOpenChange }: EmbeddingPreviewModalProps) => {
  // Mock embedding data
  const vectorPreview = [
    0.0234, -0.1456, 0.8912, 0.3421, -0.5678, 0.1234, 0.7891, -0.2345,
    0.4567, -0.6789, 0.2134, 0.9876, -0.3456, 0.5432, -0.7654, 0.1987
  ];

  const stats = {
    model: "google_vertex_ai_embedding",
    version: "text-embedding-004",
    dimensions: 768,
    indexed_documents: 203,
    avg_processing_time: "142ms",
    last_indexed: "Oct 15, 2024 10:30 AM",
    index_name: "adopter_applications"
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" />
            Vector Embedding Preview
          </DialogTitle>
        </DialogHeader>

        <ScrollArea className="max-h-[600px] pr-4">
          <div className="space-y-4">
            {/* Model Info */}
            <div className="bg-muted/50 rounded-lg p-4 space-y-3">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-semibold text-foreground flex items-center gap-2">
                  <Database className="h-4 w-4 text-primary" />
                  Model Configuration
                </h4>
                <Badge variant="outline" className="font-mono text-xs">
                  {stats.version}
                </Badge>
              </div>
              
              <div className="grid grid-cols-2 gap-3 text-xs">
                <div>
                  <p className="text-muted-foreground mb-1">Model</p>
                  <p className="text-foreground font-mono">{stats.model}</p>
                </div>
                <div>
                  <p className="text-muted-foreground mb-1">Dimensions</p>
                  <p className="text-foreground font-semibold">{stats.dimensions}</p>
                </div>
                <div>
                  <p className="text-muted-foreground mb-1">Indexed Documents</p>
                  <p className="text-foreground font-semibold">{stats.indexed_documents}</p>
                </div>
                <div>
                  <p className="text-muted-foreground mb-1">Avg Processing Time</p>
                  <p className="text-foreground font-mono">{stats.avg_processing_time}</p>
                </div>
              </div>
            </div>

            {/* Elasticsearch Index */}
            <div className="bg-muted/50 rounded-lg p-4">
              <h4 className="text-sm font-semibold text-foreground flex items-center gap-2 mb-3">
                <Layers className="h-4 w-4 text-success" />
                Elasticsearch Index
              </h4>
              <div className="space-y-2 text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">Index Name:</span>
                  <span className="text-foreground font-mono">{stats.index_name}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">Last Indexed:</span>
                  <span className="text-foreground">{stats.last_indexed}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">Vector Field:</span>
                  <span className="text-foreground font-mono">application_embedding</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">Similarity:</span>
                  <span className="text-foreground font-mono">cosine</span>
                </div>
              </div>
            </div>

            {/* Vector Preview */}
            <div className="bg-muted/50 rounded-lg p-4">
              <h4 className="text-sm font-semibold text-foreground mb-3">
                Sample Vector (first 16 of {stats.dimensions} dimensions)
              </h4>
              <div className="bg-card border border-border rounded p-3 font-mono text-xs">
                <div className="flex flex-wrap gap-2">
                  {vectorPreview.map((val, idx) => (
                    <span 
                      key={idx}
                      className={`px-2 py-1 rounded ${
                        val > 0 
                          ? 'bg-success/10 text-success' 
                          : 'bg-destructive/10 text-destructive'
                      }`}
                    >
                      {val > 0 ? '+' : ''}{val.toFixed(4)}
                    </span>
                  ))}
                  <span className="text-muted-foreground self-center">
                    ... +{stats.dimensions - vectorPreview.length} more
                  </span>
                </div>
              </div>
              <p className="text-xs text-muted-foreground mt-2">
                Each document is transformed into a {stats.dimensions}-dimensional vector for semantic search.
              </p>
            </div>

            {/* Technical Details */}
            <div className="border border-border rounded-lg p-4">
              <h4 className="text-sm font-semibold text-foreground mb-3">Technical Details</h4>
              <div className="space-y-2 text-xs text-muted-foreground">
                <p>
                  • <span className="font-semibold text-foreground">Dense vectors</span> enable semantic similarity search beyond keyword matching
                </p>
                <p>
                  • <span className="font-semibold text-foreground">Cosine similarity</span> measures the angle between vectors (0 = unrelated, 1 = identical)
                </p>
                <p>
                  • <span className="font-semibold text-foreground">768 dimensions</span> capture nuanced meaning from the Vertex AI text-embedding-004 model
                </p>
                <p>
                  • <span className="font-semibold text-foreground">Elasticsearch kNN</span> efficiently searches millions of vectors in milliseconds
                </p>
              </div>
            </div>
          </div>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  );
};
