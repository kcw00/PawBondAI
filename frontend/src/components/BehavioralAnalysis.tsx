import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { CheckCircle, AlertTriangle, Search, TrendingUp } from "lucide-react";

interface BehavioralAnalysisProps {
  data: {
    dogName: string;
    week: number;
    triggers: Array<{ text: string; severity: "high" | "medium" | "low" }>;
    improvements: string[];
    similarCases: Array<{
      dogName: string;
      breed: string;
      adoptionDate: string;
      similarity: number;
      weekThreeReport: string;
      timeline: Array<{ week: number; milestone: string }>;
      outcome: string;
      outcomeSuccess: boolean;
    }>;
    predictions: {
      expectedTimeline: Array<{ weeks: string; milestone: string }>;
      successRate: number;
      totalSimilarCases: number;
    };
    recommendedAdopter: string[];
  };
}

export const BehavioralAnalysis = ({ data }: BehavioralAnalysisProps) => {
  return (
    <div className="space-y-4">
      {/* Key Findings */}
      <Card className="p-6 bg-white border-gray-200">
        <div className="flex items-center mb-4">
          <TrendingUp className="h-5 w-5 text-[#6a994e] mr-2" />
          <h3 className="text-lg font-bold text-foreground">Key Findings</h3>
        </div>

        <div className="space-y-4">
          {/* Anxiety Triggers */}
          <div>
            <p className="text-sm font-semibold text-foreground mb-2">Anxiety Triggers Detected:</p>
            <div className="space-y-2">
              {data.triggers.map((trigger, idx) => (
                <div key={idx} className="flex items-start gap-2">
                  <span className="text-destructive">🔴</span>
                  <span className="text-sm text-foreground">{trigger.text}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Positive Progress */}
          <div>
            <p className="text-sm font-semibold text-foreground mb-2">Positive Progress:</p>
            <div className="space-y-2">
              {data.improvements.map((improvement, idx) => (
                <div key={idx} className="flex items-start gap-2">
                  <CheckCircle className="h-4 w-4 text-[#6a994e] mt-0.5" />
                  <span className="text-sm text-foreground">{improvement}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="text-sm text-muted-foreground pt-2 border-t">
            Timeline: Week {data.week} (typical for anxious rescues)
          </div>
        </div>
      </Card>

      {/* Similar Cases */}
      <Card className="p-6 bg-white border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <Search className="h-5 w-5 text-[#CFE1B9] mr-2" />
            <h3 className="text-lg font-bold text-foreground">Similar Cases from Elasticsearch</h3>
          </div>
          <Badge variant="secondary" className="bg-[#CFE1B9]/20 text-[#718355]">
            {data.similarCases.length} matches
          </Badge>
        </div>

        <p className="text-sm text-muted-foreground mb-4">
          Found {data.similarCases.length} dogs with similar behavioral profiles:
        </p>

        <div className="space-y-4">
          {data.similarCases.map((caseItem, idx) => (
            <Card key={idx} className="p-4 bg-[#fffcf2] border-gray-200">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h4 className="font-semibold text-foreground">
                    {caseItem.dogName} - {caseItem.breed}
                  </h4>
                  <p className="text-xs text-muted-foreground">Adopted {caseItem.adoptionDate}</p>
                </div>
                <Badge variant="secondary" className="bg-[#6a994e]/20 text-[#6a994e]">
                  {caseItem.similarity}% similarity
                </Badge>
              </div>

              <div className="mb-3">
                <p className="text-xs font-semibold text-foreground mb-1">
                  Week 3 Report ({caseItem.similarity}% text similarity):
                </p>
                <p className="text-xs text-muted-foreground italic">
                  "{caseItem.weekThreeReport}"
                </p>
              </div>

              <div>
                <p className="text-xs font-semibold text-foreground mb-2">Timeline to adoption:</p>
                <div className="space-y-1">
                  {caseItem.timeline.map((item, timeIdx) => (
                    <p key={timeIdx} className="text-xs text-foreground">
                      • Week {item.week}: {item.milestone}
                    </p>
                  ))}
                  <div className="flex items-center gap-2 mt-2">
                    <span className="text-xs font-semibold text-foreground">Outcome:</span>
                    {caseItem.outcomeSuccess ? (
                      <Badge variant="secondary" className="bg-[#6a994e]/20 text-[#6a994e]">
                        ✅ {caseItem.outcome}
                      </Badge>
                    ) : (
                      <Badge variant="secondary" className="bg-destructive/20 text-destructive">
                        ❌ {caseItem.outcome}
                      </Badge>
                    )}
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </Card>

      {/* Predictions */}
      <Card className="p-6 bg-white border-gray-200">
        <div className="flex items-center mb-4">
          <TrendingUp className="h-5 w-5 text-[#718355] mr-2" />
          <h3 className="text-lg font-bold text-foreground">
            Predictions Based on Similar Cases
          </h3>
        </div>

        <div className="space-y-4">
          {/* Expected Timeline */}
          <div>
            <p className="text-sm font-semibold text-foreground mb-2">Expected Timeline:</p>
            <div className="space-y-1">
              {data.predictions.expectedTimeline.map((item, idx) => (
                <p key={idx} className="text-sm text-foreground">
                  • {item.weeks}: {item.milestone}
                </p>
              ))}
            </div>
          </div>

          {/* Success Rate */}
          <div className="flex items-center justify-between p-3 bg-[#6a994e]/10 rounded-lg">
            <span className="text-sm font-semibold text-foreground">Success Rate:</span>
            <span className="text-lg font-bold text-[#6a994e]">
              {data.predictions.successRate}%
            </span>
          </div>
          <p className="text-xs text-muted-foreground">
            Based on {data.predictions.totalSimilarCases} similar cases
          </p>

          {/* Recommended Adopter Profile */}
          <div>
            <p className="text-sm font-semibold text-foreground mb-2">
              Recommended Adopter Profile:
            </p>
            <div className="space-y-1">
              {data.recommendedAdopter.map((trait, idx) => (
                <div key={idx} className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-[#6a994e]" />
                  <span className="text-sm text-foreground">{trait}</span>
                </div>
              ))}
            </div>
          </div>

          <Button
            className="w-full mt-4 bg-[#718355] hover:bg-[#718355]/90 text-white"
          >
            <Search className="h-4 w-4 mr-2" />
            Search for Matching Adopters
          </Button>
        </div>
      </Card>
    </div>
  );
};
