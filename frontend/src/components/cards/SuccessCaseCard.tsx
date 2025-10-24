import { Dog, MapPin, Calendar, CheckCircle2, TrendingUp, ExternalLink } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useState } from "react";

interface SuccessCase {
  dogName: string;
  dogPhoto?: string;
  breed: string;
  location: string;
  adoptionDate: string;
  similarConditions: string[];
  similarityScore: number;
  journeySteps: {
    initialCondition: string;
    treatmentDuration: string;
    adopterProfile: string;
    currentStatus: string;
  };
  successFactors: string[];
  caseId?: string;
}

interface SuccessCaseCardProps {
  successCase: SuccessCase;
  onViewFullCase?: () => void;
  onSeeAdopterProfile?: () => void;
}

export const SuccessCaseCard = ({ successCase, onViewFullCase, onSeeAdopterProfile }: SuccessCaseCardProps) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const getSimilarityColor = (score: number) => {
    if (score >= 0.9) return "bg-success/20 text-success border-success/30";
    if (score >= 0.8) return "bg-warning/20 text-warning border-warning/30";
    return "bg-muted text-muted-foreground border-border";
  };

  return (
    <Card className="p-5 bg-card border-border hover:shadow-lg transition-all duration-300 animate-fade-in">
      {/* Header with Dog Info */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          {successCase.dogPhoto && (
            <div className="w-12 h-12 rounded-full overflow-hidden bg-muted">
              <img 
                src={successCase.dogPhoto} 
                alt={successCase.dogName}
                className="w-full h-full object-cover"
              />
            </div>
          )}
          <div>
            <div className="flex items-center space-x-2">
              <Dog className="h-4 w-4 text-primary" />
              <h3 className="text-base font-bold text-foreground">{successCase.dogName}</h3>
            </div>
            <p className="text-sm text-muted-foreground">{successCase.breed}</p>
            <div className="flex items-center space-x-3 text-xs text-muted-foreground mt-1">
              <span className="flex items-center">
                <MapPin className="h-3 w-3 mr-1" />
                {successCase.location}
              </span>
              <span className="flex items-center">
                <Calendar className="h-3 w-3 mr-1" />
                Adopted: {successCase.adoptionDate}
              </span>
            </div>
          </div>
        </div>

        {/* Similarity Score Badge */}
        <Badge
          className={cn(
            "border",
            getSimilarityColor(successCase.similarityScore)
          )}
        >
          {(successCase.similarityScore * 100).toFixed(0)}% Similar
        </Badge>
      </div>

      {/* Similar Conditions */}
      <div className="mb-4">
        <span className="text-xs font-semibold text-muted-foreground block mb-2">
          Similar Conditions:
        </span>
        <div className="flex flex-wrap gap-2">
          {successCase.similarConditions.map((condition, idx) => (
            <Badge 
              key={idx} 
              variant="outline" 
              className="bg-success/10 text-success border-success/30"
            >
              {condition} ✓
            </Badge>
          ))}
        </div>
      </div>

      {/* Journey Timeline */}
      <div className="mb-4 p-4 bg-primary/5 border border-primary/20 rounded-lg">
        <div className="flex items-center space-x-2 mb-3">
          <TrendingUp className="h-4 w-4 text-primary" />
          <span className="text-sm font-semibold text-primary">Journey to Adoption:</span>
        </div>
        <div className="space-y-2">
          <div className="flex items-start space-x-2">
            <span className="text-xs font-semibold text-muted-foreground min-w-[120px]">
              Initial condition:
            </span>
            <span className="text-xs text-foreground">
              {successCase.journeySteps.initialCondition}
            </span>
          </div>
          <div className="flex items-start space-x-2">
            <span className="text-xs font-semibold text-muted-foreground min-w-[120px]">
              Treatment:
            </span>
            <span className="text-xs text-foreground">
              {successCase.journeySteps.treatmentDuration}
            </span>
          </div>
          <div className="flex items-start space-x-2">
            <span className="text-xs font-semibold text-muted-foreground min-w-[120px]">
              Adopted by:
            </span>
            <span className="text-xs text-foreground">
              {successCase.journeySteps.adopterProfile}
            </span>
          </div>
          <div className="flex items-start space-x-2">
            <span className="text-xs font-semibold text-muted-foreground min-w-[120px]">
              Current status:
            </span>
            <span className="text-xs font-bold text-success">
              {successCase.journeySteps.currentStatus}
            </span>
          </div>
        </div>
      </div>

      {/* Success Factors */}
      <div 
        className={cn(
          "mb-4 p-3 bg-success/5 border border-success/20 rounded-lg transition-all duration-300",
          isExpanded ? "max-h-[500px]" : "max-h-[80px] overflow-hidden"
        )}
      >
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <CheckCircle2 className="h-4 w-4 text-success" />
            <span className="text-sm font-semibold text-success">What made it work:</span>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-xs h-6 px-2"
          >
            {isExpanded ? "Show less" : "Show all"}
          </Button>
        </div>
        <ul className="space-y-1">
          {successCase.successFactors.map((factor, idx) => (
            <li key={idx} className="text-xs text-foreground flex items-start space-x-2">
              <span className="text-success mt-0.5">•</span>
              <span>{factor}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Action Buttons */}
      <div className="flex space-x-2">
        {onViewFullCase && (
          <Button
            variant="outline"
            size="sm"
            onClick={onViewFullCase}
            className="flex-1 border-border hover:bg-muted"
          >
            <ExternalLink className="h-3 w-3 mr-1" />
            View Full Case
          </Button>
        )}
        {onSeeAdopterProfile && (
          <Button
            variant="outline"
            size="sm"
            onClick={onSeeAdopterProfile}
            className="flex-1 border-border hover:bg-muted"
          >
            See Adopter Profile
          </Button>
        )}
      </div>

      {/* Case ID Footer */}
      {successCase.caseId && (
        <div className="mt-3 pt-3 border-t border-border text-xs text-muted-foreground">
          Case ID: {successCase.caseId}
        </div>
      )}
    </Card>
  );
};
