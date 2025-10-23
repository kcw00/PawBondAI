import { useState } from "react";
import { MapPin, Home, CheckCircle2, ChevronDown, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface ApplicationMatch {
  applicantName: string;
  applicantPhoto?: string;
  matchScore: number;
  location: string;
  distance?: string;
  housing: string;
  compatibilityFactors: Array<{ icon: string; text: string }>;
  explanation: {
    semanticScore: number;
    semanticReason: string;
    structuredMatches: string[];
    pastSuccessIndicators: string[];
  };
}

interface ApplicationMatchCardProps {
  match: ApplicationMatch;
  onViewDetails?: () => void;
  onStartMatch?: () => void;
  onCompare?: () => void;
}

export const ApplicationMatchCard = ({
  match,
  onViewDetails,
  onStartMatch,
  onCompare,
}: ApplicationMatchCardProps) => {
  const [showExplanation, setShowExplanation] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  const getScoreColor = (score: number) => {
    if (score >= 90) return "success";
    if (score >= 75) return "warning";
    return "muted";
  };

  const scoreColor = getScoreColor(match.matchScore);

  return (
    <Card
      className={cn(
        "p-5 bg-card border-border transition-all duration-300 animate-fade-in",
        "hover:shadow-lg hover:scale-[1.02]",
        isExpanded && "shadow-lg"
      )}
      onMouseEnter={() => setIsExpanded(true)}
      onMouseLeave={() => setIsExpanded(false)}
    >
      {/* Header with Photo and Match Score */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          {/* Applicant Photo */}
          <div className="w-12 h-12 rounded-full bg-muted flex items-center justify-center overflow-hidden">
            {match.applicantPhoto ? (
              <img
                src={match.applicantPhoto}
                alt={match.applicantName}
                className="w-full h-full object-cover"
              />
            ) : (
              <User className="h-6 w-6 text-muted-foreground" />
            )}
          </div>

          <div>
            <h3 className="text-lg font-bold text-foreground">
              {match.applicantName}
            </h3>
            <div className="flex items-center space-x-2 text-sm text-muted-foreground">
              <span className="flex items-center">
                <MapPin className="h-3 w-3 mr-1" />
                {match.location}
              </span>
              {match.distance && (
                <span className="text-xs">• {match.distance} away</span>
              )}
            </div>
          </div>
        </div>

        {/* Match Score Badge */}
        <div
          className={cn(
            "px-4 py-2 rounded-full text-base font-bold",
            scoreColor === "success" &&
              "bg-success/20 text-success border-2 border-success/30",
            scoreColor === "warning" &&
              "bg-warning/20 text-warning border-2 border-warning/30",
            scoreColor === "muted" &&
              "bg-muted text-muted-foreground border-2 border-border"
          )}
        >
          {match.matchScore}%
        </div>
      </div>

      {/* Housing Info */}
      <div className="flex items-center text-sm text-muted-foreground mb-4">
        <Home className="h-4 w-4 mr-1" />
        {match.housing}
      </div>

      {/* Compatibility Factors */}
      <div className="space-y-2 mb-4">
        {match.compatibilityFactors.slice(0, isExpanded ? 4 : 3).map((factor, idx) => (
          <div key={idx} className="flex items-start">
            <CheckCircle2 className="h-4 w-4 text-success mr-2 mt-0.5 flex-shrink-0" />
            <span className="text-sm text-foreground">{factor.text}</span>
          </div>
        ))}
      </div>

      {/* Action Buttons */}
      <div className="flex items-center space-x-2 mb-3">
        <Button
          variant="outline"
          size="sm"
          onClick={onViewDetails}
          className="border-border hover:bg-muted"
        >
          View Details
        </Button>
        <Button
          size="sm"
          onClick={onStartMatch}
          className="bg-secondary hover:bg-secondary/90 text-secondary-foreground"
        >
          Start Match
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={onCompare}
          className="text-muted-foreground hover:text-foreground"
        >
          Compare
        </Button>
      </div>

      {/* Why This Match Toggle */}
      <button
        onClick={() => setShowExplanation(!showExplanation)}
        className="flex items-center text-sm text-primary hover:text-primary/80 transition-colors w-full pt-3 border-t border-border"
      >
        <span className="font-medium">Why this match?</span>
        <ChevronDown
          className={cn(
            "h-4 w-4 ml-1 transition-transform",
            showExplanation && "rotate-180"
          )}
        />
      </button>

      {/* Explanation Details */}
      {showExplanation && (
        <div className="mt-3 p-4 bg-muted/50 rounded-lg space-y-3 animate-accordion-down">
          {/* Semantic Score */}
          <div>
            <span className="text-xs font-semibold text-muted-foreground block mb-1">
              Semantic Similarity:
            </span>
            <span className="text-sm text-foreground">
              {match.explanation.semanticScore.toFixed(2)} - {match.explanation.semanticReason}
            </span>
          </div>

          {/* Structured Matches */}
          <div>
            <span className="text-xs font-semibold text-muted-foreground block mb-1">
              Structured Criteria Matches:
            </span>
            <ul className="text-sm text-foreground space-y-1">
              {match.explanation.structuredMatches.map((item, idx) => (
                <li key={idx} className="flex items-start">
                  <span className="text-success mr-2">✓</span>
                  {item}
                </li>
              ))}
            </ul>
          </div>

          {/* Past Success Indicators */}
          <div>
            <span className="text-xs font-semibold text-muted-foreground block mb-1">
              Past Success Indicators:
            </span>
            <ul className="text-sm text-foreground space-y-1">
              {match.explanation.pastSuccessIndicators.map((item, idx) => (
                <li key={idx} className="flex items-start">
                  <span className="text-warning mr-2">★</span>
                  {item}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Powered by Badge */}
      <div className="mt-3 pt-3 border-t border-border">
        <span className="text-xs text-muted-foreground">Powered by Elasticsearch</span>
      </div>
    </Card>
  );
};
