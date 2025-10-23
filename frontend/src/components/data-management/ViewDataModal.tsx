import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { X, ChevronDown, ChevronRight } from "lucide-react";

interface ViewDataModalProps {
  open: boolean;
  onClose: () => void;
  data: any[];
  type: 'applications' | 'dogs' | 'cases' | 'medical';
}

export const ViewDataModal = ({ open, onClose, data, type }: ViewDataModalProps) => {
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set());

  const toggleRow = (index: number) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedRows(newExpanded);
  };

  const getTitle = () => {
    switch (type) {
      case 'applications':
        return 'Indexed Applications';
      case 'dogs':
        return 'Indexed Dog Profiles';
      case 'cases':
        return 'Indexed Outcomes';
      case 'medical':
        return 'Indexed Medical Documents';
    }
  };

  const getDescription = () => {
    return `Showing ${data.length} most recent ${type} from Elasticsearch`;
  };

  const renderApplicationRow = (item: any, index: number) => {
    const isExpanded = expandedRows.has(index);
    return (
      <div key={index} className="border-b border-border last:border-0">
        <div
          className="p-4 hover:bg-muted/50 cursor-pointer flex items-start justify-between"
          onClick={() => toggleRow(index)}
        >
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <h4 className="font-semibold text-foreground">{item.applicant_name || 'N/A'}</h4>
              <Badge variant="outline" className="text-xs">
                {item.status || 'Pending'}
              </Badge>
            </div>
            <p className="text-xs text-muted-foreground">{item.email || 'No email'}</p>
            {!isExpanded && (
              <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                {item.motivation?.substring(0, 100)}...
              </p>
            )}
          </div>
          <Button variant="ghost" size="sm" className="ml-2">
            {isExpanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
          </Button>
        </div>
        {isExpanded && (
          <div className="px-4 pb-4 space-y-2 text-xs">
            <div className="grid grid-cols-2 gap-2">
              <div>
                <span className="text-muted-foreground">Phone:</span>
                <span className="ml-2 text-foreground">{item.phone || 'N/A'}</span>
              </div>
              <div>
                <span className="text-muted-foreground">Housing:</span>
                <span className="ml-2 text-foreground">{item.housing_type || 'N/A'}</span>
              </div>
              <div>
                <span className="text-muted-foreground">Experience:</span>
                <span className="ml-2 text-foreground">{item.experience_level || 'N/A'}</span>
              </div>
              <div>
                <span className="text-muted-foreground">Has Yard:</span>
                <span className="ml-2 text-foreground">{item.has_yard ? 'Yes' : 'No'}</span>
              </div>
            </div>
            {item.motivation && (
              <div className="mt-2 p-2 bg-muted/30 rounded">
                <p className="text-muted-foreground font-semibold mb-1">Motivation:</p>
                <p className="text-foreground">{item.motivation}</p>
              </div>
            )}
            <div className="text-muted-foreground text-[10px] mt-2">
              ID: {item.id}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderDogRow = (item: any, index: number) => {
    const isExpanded = expandedRows.has(index);
    
    // Debug log to see what data we're getting
    console.log('Dog item:', item);
    
    return (
      <div key={index} className="border-b border-border last:border-0">
        <div
          className="p-4 hover:bg-muted/50 cursor-pointer flex items-start justify-between"
          onClick={() => toggleRow(index)}
        >
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <h4 className="font-semibold text-foreground">{item.name || 'N/A'}</h4>
              <Badge variant="outline" className="text-xs">
                {item.adoption_status || 'available'}
              </Badge>
            </div>
            <p className="text-xs text-muted-foreground">
              {item.breed || 'Unknown breed'} • {item.age ? `${item.age} years` : 'Age unknown'}
            </p>
            {!isExpanded && (item.behavioral_notes || item.combined_profile) && (
              <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                {(item.behavioral_notes || item.combined_profile || '').substring(0, 100)}...
              </p>
            )}
          </div>
          <Button variant="ghost" size="sm" className="ml-2">
            {isExpanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
          </Button>
        </div>
        {isExpanded && (
          <div className="px-4 pb-4 space-y-2 text-xs">
            <div className="grid grid-cols-2 gap-2">
              <div>
                <span className="text-muted-foreground">Weight:</span>
                <span className="ml-2 text-foreground">{item.weight_kg ? `${item.weight_kg} kg` : 'N/A'}</span>
              </div>
              <div>
                <span className="text-muted-foreground">Sex:</span>
                <span className="ml-2 text-foreground">{item.sex || 'N/A'}</span>
              </div>
              {item.rescue_date && (
                <div>
                  <span className="text-muted-foreground">Rescue Date:</span>
                  <span className="ml-2 text-foreground">{new Date(item.rescue_date).toLocaleDateString()}</span>
                </div>
              )}
              {item.adoption_readiness && (
                <div>
                  <span className="text-muted-foreground">Readiness:</span>
                  <span className="ml-2 text-foreground">{item.adoption_readiness}</span>
                </div>
              )}
            </div>
            {item.behavioral_notes && (
              <div className="mt-2 p-2 bg-muted/30 rounded">
                <p className="text-muted-foreground font-semibold mb-1">Behavioral Notes:</p>
                <p className="text-foreground">{item.behavioral_notes}</p>
              </div>
            )}
            {item.combined_profile && (
              <div className="mt-2 p-2 bg-muted/30 rounded">
                <p className="text-muted-foreground font-semibold mb-1">Combined Profile:</p>
                <p className="text-foreground">{item.combined_profile}</p>
              </div>
            )}
            {item.medical_history && (
              <div className="mt-2 p-2 bg-warning/10 rounded">
                <p className="text-muted-foreground font-semibold mb-1">Medical History:</p>
                <p className="text-foreground">{item.medical_history}</p>
              </div>
            )}
            {item.active_treatments && item.active_treatments.length > 0 && (
              <div className="mt-2 p-2 bg-primary/10 rounded">
                <p className="text-muted-foreground font-semibold mb-1">Active Treatments:</p>
                <ul className="list-disc list-inside text-foreground">
                  {item.active_treatments.map((treatment: string, idx: number) => (
                    <li key={idx}>{treatment}</li>
                  ))}
                </ul>
              </div>
            )}
            <div className="text-muted-foreground text-[10px] mt-2">
              ID: {item.id}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderOutcomeRow = (item: any, index: number) => {
    const isExpanded = expandedRows.has(index);
    const isSuccess = item.outcome === 'success';
    return (
      <div key={index} className="border-b border-border last:border-0">
        <div
          className="p-4 hover:bg-muted/50 cursor-pointer flex items-start justify-between"
          onClick={() => toggleRow(index)}
        >
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <h4 className="font-semibold text-foreground">
                {item.outcome_reason || 'Outcome Record'}
              </h4>
              <Badge 
                variant="outline" 
                className={`text-xs ${isSuccess ? 'bg-success/20 text-success border-success/30' : 'bg-destructive/20 text-destructive border-destructive/30'}`}
              >
                {item.outcome || 'N/A'}
              </Badge>
            </div>
            <p className="text-xs text-muted-foreground">
              Dog: {item.dog_id || 'N/A'} • Application: {item.application_id || 'N/A'}
            </p>
            {!isExpanded && (
              <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                {(item.success_factors || item.failure_factors || '').substring(0, 100)}...
              </p>
            )}
          </div>
          <Button variant="ghost" size="sm" className="ml-2">
            {isExpanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
          </Button>
        </div>
        {isExpanded && (
          <div className="px-4 pb-4 space-y-2 text-xs">
            <div className="grid grid-cols-2 gap-2">
              {item.adopter_satisfaction_score && (
                <div>
                  <span className="text-muted-foreground">Satisfaction:</span>
                  <span className="ml-2 text-foreground">{item.adopter_satisfaction_score}/10</span>
                </div>
              )}
              {item.match_score_at_adoption && (
                <div>
                  <span className="text-muted-foreground">Match Score:</span>
                  <span className="ml-2 text-foreground">{item.match_score_at_adoption}</span>
                </div>
              )}
              {item.dog_difficulty_level && (
                <div>
                  <span className="text-muted-foreground">Dog Difficulty:</span>
                  <span className="ml-2 text-foreground">{item.dog_difficulty_level}</span>
                </div>
              )}
              {item.adopter_experience_level && (
                <div>
                  <span className="text-muted-foreground">Adopter Experience:</span>
                  <span className="ml-2 text-foreground">{item.adopter_experience_level}</span>
                </div>
              )}
            </div>
            {item.success_factors && (
              <div className="mt-2 p-2 bg-success/10 rounded">
                <p className="text-muted-foreground font-semibold mb-1">Success Factors:</p>
                <p className="text-foreground">{item.success_factors}</p>
              </div>
            )}
            {item.failure_factors && (
              <div className="mt-2 p-2 bg-destructive/10 rounded">
                <p className="text-muted-foreground font-semibold mb-1">Failure Factors:</p>
                <p className="text-foreground">{item.failure_factors}</p>
              </div>
            )}
            <div className="text-muted-foreground text-[10px] mt-2">
              ID: {item.outcome_id || item.id}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderMedicalRow = (item: any, index: number) => {
    const isExpanded = expandedRows.has(index);
    return (
      <div key={index} className="border-b border-border last:border-0">
        <div
          className="p-4 hover:bg-muted/50 cursor-pointer flex items-start justify-between"
          onClick={() => toggleRow(index)}
        >
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <h4 className="font-semibold text-foreground">{item.title || 'Untitled Document'}</h4>
              <Badge variant="outline" className="text-xs">
                {item.document_type || 'other'}
              </Badge>
              {item.severity && (
                <Badge 
                  variant="outline" 
                  className={`text-xs ${
                    item.severity === 'emergency' ? 'bg-destructive/20 text-destructive border-destructive/30' :
                    item.severity === 'severe' ? 'bg-warning/20 text-warning border-warning/30' :
                    'bg-muted/20'
                  }`}
                >
                  {item.severity}
                </Badge>
              )}
            </div>
            <p className="text-xs text-muted-foreground">
              Dog: {item.dog_name || 'N/A'} • {item.filename || 'No filename'}
            </p>
            {!isExpanded && item.notes && (
              <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                {item.notes.substring(0, 100)}...
              </p>
            )}
          </div>
          <Button variant="ghost" size="sm" className="ml-2">
            {isExpanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
          </Button>
        </div>
        {isExpanded && (
          <div className="px-4 pb-4 space-y-2 text-xs">
            <div className="grid grid-cols-2 gap-2">
              {item.veterinarian_name && (
                <div>
                  <span className="text-muted-foreground">Veterinarian:</span>
                  <span className="ml-2 text-foreground">{item.veterinarian_name}</span>
                </div>
              )}
              {item.clinic_name && (
                <div>
                  <span className="text-muted-foreground">Clinic:</span>
                  <span className="ml-2 text-foreground">{item.clinic_name}</span>
                </div>
              )}
              {item.document_date && (
                <div>
                  <span className="text-muted-foreground">Date:</span>
                  <span className="ml-2 text-foreground">{new Date(item.document_date).toLocaleDateString()}</span>
                </div>
              )}
              {item.category && (
                <div>
                  <span className="text-muted-foreground">Category:</span>
                  <span className="ml-2 text-foreground">{item.category}</span>
                </div>
              )}
              {item.file_type && (
                <div>
                  <span className="text-muted-foreground">File Type:</span>
                  <span className="ml-2 text-foreground">{item.file_type.toUpperCase()}</span>
                </div>
              )}
              {item.file_size && (
                <div>
                  <span className="text-muted-foreground">File Size:</span>
                  <span className="ml-2 text-foreground">{(item.file_size / 1024).toFixed(2)} KB</span>
                </div>
              )}
            </div>
            {item.notes && (
              <div className="mt-2 p-2 bg-muted/30 rounded">
                <p className="text-muted-foreground font-semibold mb-1">Notes:</p>
                <p className="text-foreground">{item.notes}</p>
              </div>
            )}
            {item.content && (
              <div className="mt-2 p-2 bg-muted/30 rounded max-h-32 overflow-y-auto">
                <p className="text-muted-foreground font-semibold mb-1">Extracted Content:</p>
                <p className="text-foreground text-[10px] whitespace-pre-wrap">{item.content.substring(0, 500)}{item.content.length > 500 ? '...' : ''}</p>
              </div>
            )}
            <div className="text-muted-foreground text-[10px] mt-2">
              ID: {item.id}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderRow = (item: any, index: number) => {
    switch (type) {
      case 'applications':
        return renderApplicationRow(item, index);
      case 'dogs':
        return renderDogRow(item, index);
      case 'cases':
        return renderOutcomeRow(item, index);
      case 'medical':
        return renderMedicalRow(item, index);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[80vh] p-0">
        <DialogHeader className="p-6 pb-4">
          <DialogTitle>{getTitle()}</DialogTitle>
          <DialogDescription className="mt-1">
            {getDescription()}
          </DialogDescription>
        </DialogHeader>

        <ScrollArea className="max-h-[calc(80vh-120px)]">
          {data.length === 0 ? (
            <div className="p-8 text-center text-muted-foreground">
              No data found. Upload some files to get started!
            </div>
          ) : (
            <div className="divide-y divide-border">
              {data.map((item, index) => renderRow(item, index))}
            </div>
          )}
        </ScrollArea>

        <div className="p-4 border-t border-border bg-muted/30">
          <p className="text-xs text-muted-foreground text-center">
            Click on any row to expand and view full details
          </p>
        </div>
      </DialogContent>
    </Dialog>
  );
};
