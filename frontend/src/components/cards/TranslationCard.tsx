import { useState } from "react";
import { Languages, ChevronDown, AlertCircle } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface Translation {
  originalLanguage: string;
  originalLanguageCode: string;
  originalText: string;
  translatedText: string;
  medicalTerms: Array<{ term: string; position: number }>;
  confidenceScore: number;
}

interface TranslationCardProps {
  translation: Translation;
}

export const TranslationCard = ({ translation }: TranslationCardProps) => {
  const [showOriginal, setShowOriginal] = useState(false);

  const highlightMedicalTerms = (text: string) => {
    let result = text;
    const sortedTerms = [...translation.medicalTerms].sort(
      (a, b) => b.position - a.position
    );

    sortedTerms.forEach((item) => {
      const { term, position } = item;
      result =
        result.substring(0, position) +
        `<mark class="bg-warning/30 text-foreground font-semibold px-1 rounded">${term}</mark>` +
        result.substring(position + term.length);
    });

    return result;
  };

  const getConfidenceColor = (score: number) => {
    if (score >= 90) return "success";
    if (score >= 75) return "warning";
    return "destructive";
  };

  const confidenceColor = getConfidenceColor(translation.confidenceScore);

  return (
    <Card className="p-5 bg-card border-border shadow-sm animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Languages className="h-5 w-5 text-primary" />
          <h3 className="text-lg font-bold text-foreground">Translation</h3>
        </div>
        <Badge
          className={cn(
            "border",
            confidenceColor === "success" &&
              "bg-success/20 text-success border-success/30",
            confidenceColor === "warning" &&
              "bg-warning/20 text-warning border-warning/30",
            confidenceColor === "destructive" &&
              "bg-destructive/20 text-destructive border-destructive/30"
          )}
        >
          {translation.confidenceScore}% Confidence
        </Badge>
      </div>

      {/* Language Flag and Toggle */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <span className="text-2xl">
            {translation.originalLanguageCode === "ko" ? "🇰🇷" : "🌐"}
          </span>
          <span className="text-sm font-medium text-muted-foreground">
            {translation.originalLanguage}
          </span>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setShowOriginal(!showOriginal)}
          className="text-xs"
        >
          {showOriginal ? "Show Translated" : "Show Original"}
        </Button>
      </div>

      {/* Original Text Preview (if showing original) */}
      {showOriginal ? (
        <div className="mb-4 p-4 bg-muted/50 border border-border rounded-lg">
          <p className="text-sm text-foreground whitespace-pre-line">
            {translation.originalText}
          </p>
        </div>
      ) : (
        <>
          {/* Translation Arrow */}
          <div className="flex items-center justify-center mb-3">
            <ChevronDown className="h-5 w-5 text-muted-foreground" />
          </div>

          {/* Translated Text with Highlighted Medical Terms */}
          <div className="mb-4 p-4 bg-primary/5 border border-primary/20 rounded-lg">
            <p
              className="text-sm text-foreground whitespace-pre-line"
              dangerouslySetInnerHTML={{
                __html: highlightMedicalTerms(translation.translatedText),
              }}
            />
          </div>

          {/* Medical Terms Legend */}
          {translation.medicalTerms.length > 0 && (
            <div className="mb-4 p-3 bg-warning/5 border border-warning/20 rounded-lg flex items-start">
              <AlertCircle className="h-4 w-4 text-warning mr-2 mt-0.5 flex-shrink-0" />
              <div>
                <span className="text-xs font-semibold text-warning block mb-1">
                  Medical Terms Highlighted
                </span>
                <span className="text-xs text-muted-foreground">
                  {translation.medicalTerms.length} medical term(s) identified in this
                  document
                </span>
              </div>
            </div>
          )}
        </>
      )}

      {/* Powered by Badge */}
      <div className="pt-3 border-t border-border flex items-center justify-between">
        <span className="text-xs text-muted-foreground">
          Powered by Google Cloud Translation
        </span>
        <img
          src="https://cloud.google.com/_static/cloud/images/social-icon-google-cloud-1200-630.png"
          alt="Google Cloud"
          className="h-4 opacity-50"
        />
      </div>
    </Card>
  );
};
