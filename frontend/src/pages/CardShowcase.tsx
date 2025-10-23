import { ApplicationMatchCard } from "@/components/cards/ApplicationMatchCard";
import { DogProfileCard } from "@/components/cards/DogProfileCard";
import { SearchExplanationCard } from "@/components/cards/SearchExplanationCard";
import { TranslationCard } from "@/components/cards/TranslationCard";
import { CaseStudyCard } from "@/components/cards/CaseStudyCard";
import { SuccessCaseCard } from "@/components/cards/SuccessCaseCard";
import { PhotoAnalysisCard } from "@/components/cards/PhotoAnalysisCard";
import { MedicalDocumentCard } from "@/components/cards/MedicalDocumentCard";
import {
  mockApplicationMatches,
  mockDogProfiles,
  mockSearchExplanations,
  mockTranslations,
  mockCaseStudies,
  mockSuccessCases,
  mockPhotoAnalysis,
  mockMedicalDocument,
} from "@/data/mockCardData";

export default function CardShowcase() {
  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-4xl mx-auto space-y-12">
        <div>
          <h1 className="text-4xl font-bold mb-2 text-foreground">Card Components Showcase</h1>
          <p className="text-muted-foreground">Testing all reusable card components with mock data</p>
        </div>

        {/* Application Match Cards */}
        <section>
          <h2 className="text-2xl font-semibold mb-4 text-foreground">Application Match Cards</h2>
          <div className="space-y-4">
            {mockApplicationMatches.map((match, index) => (
              <ApplicationMatchCard
                key={index}
                match={match}
                onViewDetails={() => console.log("View details:", match.applicantName)}
                onStartMatch={() => console.log("Start match:", match.applicantName)}
                onCompare={() => console.log("Compare:", match.applicantName)}
              />
            ))}
          </div>
        </section>

        {/* Dog Profile Cards */}
        <section>
          <h2 className="text-2xl font-semibold mb-4 text-foreground">Dog Profile Cards</h2>
          <div className="space-y-4">
            {mockDogProfiles.map((dog, index) => (
              <DogProfileCard
                key={index}
                dog={dog}
                onViewProfile={() => console.log("View profile:", dog.name)}
                onFindMatches={() => console.log("Find matches:", dog.name)}
                onTranslate={() => console.log("Translate:", dog.name)}
              />
            ))}
          </div>
        </section>

        {/* Search Explanation Cards */}
        <section>
          <h2 className="text-2xl font-semibold mb-4 text-foreground">Search Explanation Cards</h2>
          <div className="space-y-4">
            {mockSearchExplanations.map((explanation, index) => (
              <SearchExplanationCard
                key={index}
                explanation={explanation}
              />
            ))}
          </div>
        </section>

        {/* Translation Cards */}
        <section>
          <h2 className="text-2xl font-semibold mb-4 text-foreground">Translation Cards</h2>
          <div className="space-y-4">
            {mockTranslations.map((translation, index) => (
              <TranslationCard
                key={index}
                translation={translation}
              />
            ))}
          </div>
        </section>

        {/* Case Study Cards */}
        <section>
          <h2 className="text-2xl font-semibold mb-4 text-foreground">Case Study Cards</h2>
          <div className="space-y-4">
            {mockCaseStudies.map((caseStudy, index) => (
              <CaseStudyCard
                key={index}
                caseStudy={caseStudy}
                onViewFullCase={() => console.log("View full case:", caseStudy.caseId)}
              />
            ))}
          </div>
        </section>

        {/* Success Case Cards */}
        <section>
          <h2 className="text-2xl font-semibold mb-4 text-foreground">Success Case Cards (Medical Match)</h2>
          <p className="text-sm text-muted-foreground mb-4">
            Shows similar successful adoptions for dogs with medical conditions
          </p>
          <div className="space-y-4">
            {mockSuccessCases.map((successCase, index) => (
              <SuccessCaseCard
                key={index}
                successCase={successCase}
                onViewFullCase={() => console.log("View full case:", successCase.caseId)}
                onSeeAdopterProfile={() => console.log("View adopter profile")}
              />
            ))}
          </div>
        </section>

        {/* Photo Analysis Card */}
        <section>
          <h2 className="text-2xl font-semibold mb-4 text-foreground">Photo Analysis Card</h2>
          <p className="text-sm text-muted-foreground mb-4">
            AI-powered photo analysis using Google Cloud Vision API
          </p>
          <PhotoAnalysisCard analysis={mockPhotoAnalysis} />
        </section>

        {/* Medical Document Card */}
        <section>
          <h2 className="text-2xl font-semibold mb-4 text-foreground">Medical Document Card</h2>
          <p className="text-sm text-muted-foreground mb-4">
            Processed medical records with translation and analysis
          </p>
          <MedicalDocumentCard document={mockMedicalDocument} isProcessing={false} />
        </section>
      </div>
    </div>
  );
}
