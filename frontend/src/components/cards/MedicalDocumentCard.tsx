import { FileText, CheckCircle2, AlertTriangle, Pill, Calendar, Activity } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";

interface MedicalCondition {
  name: string;
  severity: "critical" | "moderate" | "mild";
  status: "active" | "resolved" | "monitoring";
}

interface Treatment {
  medication: string;
  dosage: string;
  frequency: string;
  startDate: string;
  duration: string;
}

interface MedicalDocument {
  documentUrl?: string;
  dogName: string;
  processingSteps: {
    ocrComplete: boolean;
    translationComplete: boolean;
    conditionsIdentified: boolean;
    casesSearched: boolean;
  };
  primaryConditions: MedicalCondition[];
  treatments: Treatment[];
  followUpSchedule: string;
  prognosis: string;
  prognosisConfidence: number;
  adoptionConsiderations: string[];
  estimatedMonthlyCost: number;
}

interface MedicalDocumentCardProps {
  document: MedicalDocument;
  isProcessing?: boolean;
}

export const MedicalDocumentCard = ({ document, isProcessing = false }: MedicalDocumentCardProps) => {
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical":
        return "bg-destructive/20 text-destructive border-destructive/30";
      case "moderate":
        return "bg-warning/20 text-warning border-warning/30";
      case "mild":
        return "bg-primary/20 text-primary border-primary/30";
      default:
        return "bg-muted text-muted-foreground border-border";
    }
  };

  const getStatusIcon = (completed: boolean) => {
    return completed ? (
      <CheckCircle2 className="h-4 w-4 text-success" />
    ) : (
      <div className="h-4 w-4 rounded-full border-2 border-muted animate-pulse" />
    );
  };

  return (
    <Card className="p-5 bg-card border-border shadow-lg animate-fade-in">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-2">
          <span className="text-2xl">📋</span>
          <div>
            <h3 className="text-base font-bold text-foreground">
              Medical Summary
            </h3>
            <p className="text-xs text-muted-foreground">
              {document.dogName}'s veterinary record (translated from Korean)
            </p>
          </div>
        </div>
      </div>

      <div className="border-b border-border mb-4"></div>

      {/* Processing Steps */}
      {isProcessing && (
        <div className="mb-4 p-4 bg-muted/30 border border-border rounded-lg">
          <p className="text-sm font-semibold text-foreground mb-3">⏳ Processing {document.dogName.toLowerCase()}_vet_record.pdf</p>
          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              {getStatusIcon(document.processingSteps.ocrComplete)}
              <span className="text-sm text-foreground">Extracting text with OCR...</span>
            </div>
            <div className="flex items-center space-x-2">
              {getStatusIcon(document.processingSteps.translationComplete)}
              <span className="text-sm text-foreground">Translating from Korean...</span>
            </div>
            <div className="flex items-center space-x-2">
              {getStatusIcon(document.processingSteps.conditionsIdentified)}
              <span className="text-sm text-foreground">Identifying conditions...</span>
            </div>
            <div className="flex items-center space-x-2">
              {getStatusIcon(document.processingSteps.casesSearched)}
              <span className="text-sm text-foreground">Searching similar cases...</span>
            </div>
          </div>
        </div>
      )}

      {/* Primary Conditions */}
      <div className="mb-4">
        <div className="flex items-center space-x-2 mb-2">
          <span className="text-lg">🔴</span>
          <span className="text-sm font-bold text-foreground">Primary Conditions:</span>
        </div>
        <ul className="space-y-1 ml-7">
          {document.primaryConditions.map((condition, idx) => (
            <li key={idx} className="text-sm text-foreground">
              • {condition.name}
            </li>
          ))}
        </ul>
      </div>

      {/* Treatment */}
      <div className="mb-4">
        <div className="flex items-center space-x-2 mb-2">
          <span className="text-lg">💊</span>
          <span className="text-sm font-bold text-foreground">Treatment:</span>
        </div>
        <ul className="space-y-1 ml-7">
          {document.treatments.map((treatment, idx) => (
            <li key={idx} className="text-sm text-foreground">
              • {treatment.medication} ({treatment.frequency})
            </li>
          ))}
          {document.treatments[0] && (
            <li className="text-sm text-foreground">
              • Started: {document.treatments[0].startDate}
            </li>
          )}
        </ul>
      </div>

      {/* Duration & Follow-up */}
      <div className="mb-4 space-y-2">
        {document.treatments[0] && (
          <div className="flex items-start space-x-2">
            <span className="text-lg">📅</span>
            <div>
              <span className="text-sm font-bold text-foreground">Duration: </span>
              <span className="text-sm text-foreground">{document.treatments[0].duration}</span>
            </div>
          </div>
        )}
        <div className="flex items-start space-x-2">
          <span className="text-lg">🏥</span>
          <div>
            <span className="text-sm font-bold text-foreground">Follow-up: </span>
            <span className="text-sm text-foreground">{document.followUpSchedule}</span>
          </div>
        </div>
        <div className="flex items-start space-x-2">
          <span className="text-lg">✅</span>
          <div>
            <span className="text-sm font-bold text-foreground">Prognosis: </span>
            <span className="text-sm text-foreground">{document.prognosis}</span>
          </div>
        </div>
      </div>

      {/* Adoption Considerations */}
      <div className="p-4 bg-warning/5 border border-warning/20 rounded-lg">
        <div className="flex items-center space-x-2 mb-3">
          <span className="text-lg">⚠️</span>
          <span className="text-sm font-bold text-warning">Adoption Considerations:</span>
        </div>
        <ul className="space-y-1 ml-7">
          {document.adoptionConsiderations.map((consideration, idx) => (
            <li key={idx} className="text-sm text-foreground">
              • {consideration}
            </li>
          ))}
        </ul>
      </div>
    </Card>
  );
};
