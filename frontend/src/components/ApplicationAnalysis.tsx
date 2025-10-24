import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2, TrendingUp, AlertCircle, Heart, FileText } from "lucide-react";
import { Link } from "react-router-dom";

interface SimilarAdopter {
  name: string;
  similarity: number;
  dogName: string;
  dogAge: number;
  adoptionDate: string;
  outcome: "successful" | "returned";
  traits: string[];
  followUp: string[];
  successFactors: string[];
}

interface DogMatch {
  id: string;
  name: string;
  breed: string;
  age: number;
  matchScore: number;
  reasons: string[];
  similarPairing?: string;
}

interface ApplicationAnalysisProps {
  applicantName: string;
  strengths: string[];
  experienceLevel: string;
  bestSuitedFor: string[];
  similarAdopters: SimilarAdopter[];
  successRate: number;
  successFactors: Record<string, number>;
  recommendedDogs: DogMatch[];
  onViewQuery?: () => void;
}

export const ApplicationAnalysis = ({
  applicantName,
  strengths,
  experienceLevel,
  bestSuitedFor,
  similarAdopters,
  successRate,
  successFactors,
  recommendedDogs,
  onViewQuery,
}: ApplicationAnalysisProps) => {
  return (
    <div className="space-y-6 animate-fade-in">
      {/* Applicant Profile */}
      <Card className="p-6 bg-[#CFE1B9]/10 border-[#CFE1B9]">
        <div className="flex items-center mb-4">
          <FileText className="h-5 w-5 text-[#718355] mr-2" />
          <h3 className="text-xl font-bold text-foreground">Applicant Profile</h3>
        </div>

        <div className="space-y-4">
          <div>
            <p className="text-sm font-semibold text-foreground mb-2">Key Strengths:</p>
            <div className="space-y-2">
              {strengths.map((strength, idx) => (
                <div key={idx} className="flex items-start">
                  <CheckCircle2 className="h-4 w-4 text-[#6a994e] mr-2 mt-0.5 flex-shrink-0" />
                  <p className="text-sm text-foreground">{strength}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="flex gap-4 pt-2">
            <div>
              <p className="text-xs text-muted-foreground mb-1">Experience Level</p>
              <Badge className="bg-[#718355] text-white">{experienceLevel}</Badge>
            </div>
            <div>
              <p className="text-xs text-muted-foreground mb-1">Best suited for</p>
              <div className="flex gap-1 flex-wrap">
                {bestSuitedFor.map((trait, idx) => (
                  <Badge key={idx} variant="outline" className="border-[#718355] text-[#718355]">
                    {trait}
                  </Badge>
                ))}
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* Similar Past Adopters */}
      <div>
        <div className="flex items-center mb-3">
          <TrendingUp className="h-5 w-5 text-[#718355] mr-2" />
          <h3 className="text-xl font-bold text-foreground">Similar Past Adopters</h3>
          <Badge className="ml-2 bg-[#CFE1B9] text-[#718355]">Elasticsearch vector search</Badge>
        </div>

        <div className="space-y-4">
          {similarAdopters.map((adopter, idx) => (
            <Card key={idx} className="p-5 bg-white border-gray-200 hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <p className="font-bold text-lg text-foreground">👤 {adopter.name}</p>
                  <div className="flex items-center mt-1">
                    <span className="text-sm text-muted-foreground mr-2">Similarity Score:</span>
                    <span className="text-lg font-bold text-[#6a994e]">{adopter.similarity}%</span>
                  </div>
                </div>
                <Badge className="bg-[#6a994e] text-white">
                  <CheckCircle2 className="h-3 w-3 mr-1" />
                  {adopter.outcome.toUpperCase()}
                </Badge>
              </div>

              <div className="space-y-3 text-sm">
                <div>
                  <p className="text-muted-foreground mb-1">Her application profile:</p>
                  {adopter.traits.map((trait, tidx) => (
                    <p key={tidx} className="text-foreground">• {trait}</p>
                  ))}
                </div>

                <div className="bg-[#fffcf2] p-3 rounded">
                  <p className="font-semibold text-foreground mb-1">
                    Adoption: {adopter.dogName} ({adopter.dogAge} years)
                  </p>
                  <p className="text-xs text-muted-foreground">Date: {adopter.adoptionDate}</p>
                </div>

                <div>
                  <p className="font-semibold text-foreground mb-1">Follow-up reports:</p>
                  {adopter.followUp.map((report, ridx) => (
                    <p key={ridx} className="text-muted-foreground italic mb-1">"{report}"</p>
                  ))}
                </div>

                <div>
                  <p className="font-semibold text-foreground mb-1">What made it work:</p>
                  {adopter.successFactors.map((factor, fidx) => (
                    <p key={fidx} className="text-foreground">• {factor}</p>
                  ))}
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* Pattern Analysis */}
      <Card className="p-6 bg-white border-gray-200">
        <div className="flex items-center mb-4">
          <AlertCircle className="h-5 w-5 text-[#718355] mr-2" />
          <h3 className="text-xl font-bold text-foreground">Pattern Analysis</h3>
        </div>

        <p className="text-sm text-muted-foreground mb-4">
          Based on Elasticsearch analysis of 47 similar adopters:
        </p>

        <div className="space-y-4">
          <div>
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm font-semibold text-foreground">Success Rate</p>
              <span className="text-2xl font-bold text-[#6a994e]">{successRate}%</span>
            </div>
            <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
              <div 
                className="h-full bg-[#6a994e]" 
                style={{ width: `${successRate}%` }}
              />
            </div>
          </div>

          <div>
            <p className="text-sm font-semibold text-foreground mb-2">Success Factors:</p>
            <div className="space-y-2">
              {Object.entries(successFactors).map(([factor, percentage]) => (
                <div key={factor}>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-foreground">{factor}</span>
                    <span className="font-medium text-[#718355]">{percentage}%</span>
                  </div>
                  <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-[#718355]" 
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-[#CFE1B9]/20 p-3 rounded">
            <p className="text-sm font-semibold text-foreground mb-1">Risk Factors:</p>
            <div className="flex items-center">
              <CheckCircle2 className="h-4 w-4 text-[#6a994e] mr-2" />
              <p className="text-sm text-foreground">None detected ✅</p>
            </div>
          </div>
        </div>
      </Card>

      {/* Recommended Dogs */}
      <div>
        <div className="flex items-center mb-3">
          <Heart className="h-5 w-5 text-[#f4a261] mr-2" />
          <h3 className="text-xl font-bold text-foreground">Recommended Dogs for {applicantName}</h3>
        </div>

        <div className="grid gap-4">
          {recommendedDogs.map((dog) => (
            <Card key={dog.id} className="p-5 bg-white border-gray-200 hover:shadow-lg transition-all hover:scale-[1.01]">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h4 className="font-bold text-lg text-foreground">{dog.name}</h4>
                  <p className="text-sm text-muted-foreground">{dog.breed}, {dog.age} years</p>
                </div>
                <Badge className="bg-[#6a994e] text-white text-base px-3 py-1">
                  {dog.matchScore}% Match
                </Badge>
              </div>

              <div className="space-y-3">
                <div>
                  <p className="text-sm font-semibold text-foreground mb-2">Why this match:</p>
                  {dog.reasons.map((reason, idx) => (
                    <div key={idx} className="flex items-start mb-1">
                      <CheckCircle2 className="h-4 w-4 text-[#6a994e] mr-2 mt-0.5 flex-shrink-0" />
                      <p className="text-sm text-foreground">{reason}</p>
                    </div>
                  ))}
                </div>

                {dog.similarPairing && (
                  <div className="bg-[#fffcf2] p-3 rounded">
                    <p className="text-xs font-semibold text-foreground mb-1">Similar successful pairing:</p>
                    <p className="text-xs text-muted-foreground">{dog.similarPairing}</p>
                  </div>
                )}

                <Link to={`/dogs/${dog.id}`}>
                  <Button className="w-full bg-[#f4a261] hover:bg-[#f4a261]/90 text-white">
                    View Full Profile
                  </Button>
                </Link>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3 pt-4">
        <Button variant="outline" className="flex-1 border-[#718355] text-[#718355] hover:bg-[#718355] hover:text-white">
          Compare with Other Applicants
        </Button>
        <Button className="flex-1 bg-[#f4a261] hover:bg-[#f4a261]/90 text-white">
          Draft Introduction Email
        </Button>
        {onViewQuery && (
          <Button 
            variant="outline" 
            onClick={onViewQuery}
            className="border-[#CFE1B9] text-[#718355] hover:bg-[#CFE1B9]"
          >
            View Query Details
          </Button>
        )}
      </div>
    </div>
  );
};
