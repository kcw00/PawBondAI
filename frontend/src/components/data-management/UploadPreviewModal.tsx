import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2, AlertTriangle } from "lucide-react";

interface UploadPreviewModalProps {
  open: boolean;
  onClose: () => void;
  onConfirm: () => void;
  fileName: string;
  fileType: string;
}

export const UploadPreviewModal = ({
  open,
  onClose,
  onConfirm,
  fileName,
  fileType
}: UploadPreviewModalProps) => {
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Preview: {fileName}</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* File Info */}
          <div className="p-4 bg-muted/50 rounded-lg">
            <p className="text-sm font-semibold text-foreground mb-2">File info:</p>
            <div className="space-y-1 text-sm text-muted-foreground">
              <div>• Rows detected: 203</div>
              <div>• Columns: 15</div>
              <div>• Format: CSV (UTF-8)</div>
            </div>
          </div>

          {/* Column Preview */}
          <div>
            <p className="text-sm font-semibold text-foreground mb-2">Column mapping:</p>
            <div className="border border-border rounded-lg overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-muted">
                  <tr>
                    <th className="px-4 py-2 text-left font-medium">Name</th>
                    <th className="px-4 py-2 text-left font-medium">Email</th>
                    <th className="px-4 py-2 text-left font-medium">Housing</th>
                    <th className="px-4 py-2 text-left font-medium">Has Yard</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-t border-border">
                    <td className="px-4 py-2">Sarah Chen</td>
                    <td className="px-4 py-2">sarah@example.com</td>
                    <td className="px-4 py-2">House</td>
                    <td className="px-4 py-2">Yes</td>
                  </tr>
                  <tr className="border-t border-border">
                    <td className="px-4 py-2">Mike Torres</td>
                    <td className="px-4 py-2">mike@example.com</td>
                    <td className="px-4 py-2">Apartment</td>
                    <td className="px-4 py-2">No</td>
                  </tr>
                  <tr className="border-t border-border">
                    <td className="px-4 py-2 text-muted-foreground">...</td>
                    <td className="px-4 py-2 text-muted-foreground">...</td>
                    <td className="px-4 py-2 text-muted-foreground">...</td>
                    <td className="px-4 py-2 text-muted-foreground">...</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* Validation */}
          <div>
            <p className="text-sm font-semibold text-foreground mb-2">Validation:</p>
            <div className="space-y-2">
              <div className="flex items-start gap-2">
                <CheckCircle2 className="h-4 w-4 text-success mt-0.5" />
                <span className="text-sm text-foreground">All required columns present</span>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle2 className="h-4 w-4 text-success mt-0.5" />
                <span className="text-sm text-foreground">No duplicate emails</span>
              </div>
              <div className="flex items-start gap-2">
                <AlertTriangle className="h-4 w-4 text-warning mt-0.5" />
                <div>
                  <span className="text-sm text-foreground">12 rows missing phone numbers</span>
                  <p className="text-xs text-muted-foreground">(will still index)</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={onConfirm} className="bg-primary hover:bg-primary/90">
            Upload & Index
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
