import { Eye, AlertCircle, CheckCircle2, Info } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface PhotoAnalysis {
  imageUrl: string;
  breed: string;
  breedConfidence: number;
  estimatedAge: string;
  ageIndicators: string[];
  bodyCondition: string;
  behavioralCues: string[];
  healthConcerns: string[];
  overallAssessment: "excellent" | "good" | "fair" | "needs-attention";
}

interface PhotoAnalysisCardProps {
  analysis: PhotoAnalysis;
}

export const PhotoAnalysisCard = ({ analysis }: PhotoAnalysisCardProps) => {
  const getAssessmentColor = (assessment: string) => {
    switch (assessment) {
      case "excellent":
        return "bg-success/20 text-success border-success/30";
      case "good":
        return "bg-primary/20 text-primary border-primary/30";
      case "fair":
        return "bg-warning/20 text-warning border-warning/30";
      case "needs-attention":
        return "bg-destructive/20 text-destructive border-destructive/30";
      default:
        return "bg-muted text-muted-foreground border-border";
    }
  };

  return (
    <Card className="p-5 bg-card border-border shadow-lg animate-fade-in">
      {/* Header */}
      <div className="flex items-center space-x-2 mb-4">
        <Eye className="h-5 w-5 text-primary" />
        <h3 className="text-base font-bold text-foreground">AI Photo Analysis</h3>
        <Badge className="bg-primary/20 text-primary border-primary/30 ml-auto">
          Google Cloud Vision
        </Badge>
      </div>

      {/* Image Preview */}
      <div className="mb-4 rounded-lg overflow-hidden border border-border">
        <img 
          src={analysis.imageUrl} 
          alt="Dog analysis" 
          className="w-full h-48 object-cover"
        />
      </div>

      {/* Analysis Results */}
      <div className="space-y-4">
        {/* Breed Detection */}
        <div className="p-3 bg-primary/5 border border-primary/20 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-primary">Breed Detection:</span>
            <Badge variant="outline" className="text-xs">
              {(analysis.breedConfidence * 100).toFixed(0)}% confidence
            </Badge>
          </div>
          <p className="text-sm font-semibold text-foreground">{analysis.breed}</p>
        </div>

        {/* Age Estimation */}
        <div>
          <span className="text-xs font-semibold text-muted-foreground block mb-1">
            Estimated Age:
          </span>
          <p className="text-sm text-foreground font-medium">{analysis.estimatedAge}</p>
          <div className="mt-2 space-y-1">
            {analysis.ageIndicators.map((indicator, idx) => (
              <div key={idx} className="flex items-start space-x-2">
                <Info className="h-3 w-3 text-muted-foreground mt-0.5 flex-shrink-0" />
                <span className="text-xs text-muted-foreground">{indicator}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Body Condition */}
        <div>
          <span className="text-xs font-semibold text-muted-foreground block mb-1">
            Body Condition:
          </span>
          <p className="text-sm text-foreground">{analysis.bodyCondition}</p>
        </div>

        {/* Behavioral Cues */}
        <div>
          <span className="text-xs font-semibold text-muted-foreground block mb-1">
            Behavior Signals:
          </span>
          <div className="space-y-1">
            {analysis.behavioralCues.map((cue, idx) => (
              <div key={idx} className="flex items-start space-x-2">
                <CheckCircle2 className="h-3 w-3 text-success mt-0.5 flex-shrink-0" />
                <span className="text-xs text-foreground">{cue}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Health Concerns */}
        {analysis.healthConcerns.length > 0 ? (
          <div className="p-3 bg-warning/5 border border-warning/20 rounded-lg">
            <div className="flex items-center space-x-2 mb-2">
              <AlertCircle className="h-4 w-4 text-warning" />
              <span className="text-xs font-semibold text-warning">Potential Concerns:</span>
            </div>
            <div className="space-y-1">
              {analysis.healthConcerns.map((concern, idx) => (
                <p key={idx} className="text-xs text-foreground">• {concern}</p>
              ))}
            </div>
          </div>
        ) : (
          <div className="p-3 bg-success/5 border border-success/20 rounded-lg">
            <div className="flex items-center space-x-2">
              <CheckCircle2 className="h-4 w-4 text-success" />
              <span className="text-sm text-success font-semibold">No visible concerns detected</span>
            </div>
          </div>
        )}

        {/* Overall Assessment */}
        <div className="pt-3 border-t border-border">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-muted-foreground">
              Overall Assessment:
            </span>
            <Badge className={getAssessmentColor(analysis.overallAssessment)}>
              {analysis.overallAssessment.replace("-", " ").toUpperCase()}
            </Badge>
          </div>
        </div>
      </div>
    </Card>
  );
};
