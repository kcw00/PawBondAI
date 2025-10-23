import { FileText, MapPin, Calendar, CheckCircle2, XCircle } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface CaseStudy {
  location: string;
  date: string;
  dogDescription: string;
  situation: string;
  solutionApplied: string;
  outcome: "success" | "failed";
  outcomeDetails: string;
  similarityScore: number;
  caseId?: string;
}

interface CaseStudyCardProps {
  caseStudy: CaseStudy;
  onViewFullCase?: () => void;
}

export const CaseStudyCard = ({ caseStudy, onViewFullCase }: CaseStudyCardProps) => {
  const isSuccess = caseStudy.outcome === "success";

  return (
    <Card className="p-5 bg-card border-border hover:shadow-lg transition-all duration-300 animate-fade-in">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-2">
          <FileText className="h-5 w-5 text-primary" />
          <div>
            <h3 className="text-base font-bold text-foreground">Similar Past Case</h3>
            <div className="flex items-center space-x-3 text-xs text-muted-foreground mt-1">
              <span className="flex items-center">
                <MapPin className="h-3 w-3 mr-1" />
                {caseStudy.location}
              </span>
              <span className="flex items-center">
                <Calendar className="h-3 w-3 mr-1" />
                {caseStudy.date}
              </span>
            </div>
          </div>
        </div>

        {/* Similarity Score Badge */}
        <Badge
          className={cn(
            "border",
            caseStudy.similarityScore >= 0.8
              ? "bg-success/20 text-success border-success/30"
              : caseStudy.similarityScore >= 0.6
              ? "bg-warning/20 text-warning border-warning/30"
              : "bg-muted text-muted-foreground border-border"
          )}
        >
          {(caseStudy.similarityScore * 100).toFixed(0)}% Similar
        </Badge>
      </div>

      {/* Dog Description */}
      <div className="mb-3">
        <span className="text-xs font-semibold text-muted-foreground block mb-1">
          Dog:
        </span>
        <p className="text-sm text-foreground">{caseStudy.dogDescription}</p>
      </div>

      {/* Situation */}
      <div className="mb-3">
        <span className="text-xs font-semibold text-muted-foreground block mb-1">
          Situation:
        </span>
        <p className="text-sm text-foreground">{caseStudy.situation}</p>
      </div>

      {/* Solution Applied */}
      <div className="mb-3 p-3 bg-primary/5 border border-primary/20 rounded-lg">
        <span className="text-xs font-semibold text-primary block mb-1">
          Solution Applied:
        </span>
        <p className="text-sm text-foreground">{caseStudy.solutionApplied}</p>
      </div>

      {/* Outcome */}
      <div
        className={cn(
          "mb-4 p-3 rounded-lg border",
          isSuccess
            ? "bg-success/5 border-success/20"
            : "bg-destructive/5 border-destructive/20"
        )}
      >
        <div className="flex items-center space-x-2 mb-1">
          {isSuccess ? (
            <CheckCircle2 className="h-4 w-4 text-success" />
          ) : (
            <XCircle className="h-4 w-4 text-destructive" />
          )}
          <span
            className={cn(
              "text-xs font-semibold",
              isSuccess ? "text-success" : "text-destructive"
            )}
          >
            {isSuccess ? "Successful Outcome" : "Unsuccessful Outcome"}
          </span>
        </div>
        <p className="text-sm text-foreground">{caseStudy.outcomeDetails}</p>
      </div>

      {/* View Full Case Button */}
      {onViewFullCase && (
        <Button
          variant="outline"
          size="sm"
          onClick={onViewFullCase}
          className="w-full border-border hover:bg-muted"
        >
          View Full Case
        </Button>
      )}

      {/* Powered by Badge */}
      <div className="mt-3 pt-3 border-t border-border">
        <span className="text-xs text-muted-foreground">Powered by Elasticsearch</span>
      </div>
    </Card>
  );
};
