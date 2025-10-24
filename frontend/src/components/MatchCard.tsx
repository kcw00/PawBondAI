import { MapPin, Home, CheckCircle2, ChevronDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useState } from "react";

interface Match {
  name: string;
  location: string;
  housing: string;
  score: number;
  highlights: string[];
  explanation: {
    semantic: number;
    reason: string;
    structured: string;
    experience: string;
  };
}

interface MatchCardProps {
  match: Match;
}

export const MatchCard = ({ match }: MatchCardProps) => {
  const [showExplanation, setShowExplanation] = useState(false);

  const getScoreColor = (score: number) => {
    if (score >= 90) return "success";
    if (score >= 80) return "warning";
    return "muted";
  };

  const scoreColor = getScoreColor(match.score);

  return (
    <Card className="p-5 bg-card border-border hover:shadow-lg transition-all">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center space-x-3 mb-2">
            <h3 className="text-lg font-bold text-foreground">{match.name}</h3>
            <span
              className={`px-3 py-1 rounded-full text-sm font-semibold ${
                scoreColor === "success"
                  ? "bg-success/20 text-success"
                  : scoreColor === "warning"
                  ? "bg-warning/20 text-warning"
                  : "bg-muted text-muted-foreground"
              }`}
            >
              Match Score: {match.score}%
            </span>
          </div>
          <div className="flex items-center space-x-4 text-sm text-muted-foreground">
            <span className="flex items-center">
              <MapPin className="h-4 w-4 mr-1" />
              {match.location}
            </span>
            <span className="flex items-center">
              <Home className="h-4 w-4 mr-1" />
              {match.housing}
            </span>
          </div>
        </div>
      </div>

      {/* Highlights */}
      <div className="space-y-2 mb-4">
        {match.highlights && Array.isArray(match.highlights) && match.highlights.map((highlight, idx) => (
          <div key={idx} className="flex items-start">
            <CheckCircle2 className="h-4 w-4 text-success mr-2 mt-0.5 flex-shrink-0" />
            <span className="text-sm text-foreground">{highlight}</span>
          </div>
        ))}
      </div>

      {/* Explanation Toggle */}
      <button
        onClick={() => setShowExplanation(!showExplanation)}
        className="flex items-center text-sm text-primary hover:text-primary/80 transition-colors w-full pt-3 border-t border-border"
      >
        <span className="font-medium">Why this match?</span>
        <ChevronDown
          className={`h-4 w-4 ml-1 transition-transform ${
            showExplanation ? "rotate-180" : ""
          }`}
        />
      </button>

      {/* Explanation Details */}
      {showExplanation && (
        <div className="mt-3 p-4 bg-muted/50 rounded-lg space-y-2">
          <div className="flex items-start">
            <span className="text-xs font-semibold text-muted-foreground w-32">
              Semantic Score:
            </span>
            <span className="text-xs text-foreground">
              {match.explanation.semantic} - {match.explanation.reason}
            </span>
          </div>
          <div className="flex items-start">
            <span className="text-xs font-semibold text-muted-foreground w-32">
              Structured Fit:
            </span>
            <span className="text-xs text-foreground">{match.explanation.structured}</span>
          </div>
          <div className="flex items-start">
            <span className="text-xs font-semibold text-muted-foreground w-32">
              Past Experience:
            </span>
            <span className="text-xs text-foreground">{match.explanation.experience}</span>
          </div>
        </div>
      )}
    </Card>
  );
};
