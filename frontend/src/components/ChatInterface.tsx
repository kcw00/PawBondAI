import { useState, useRef } from "react";
import { Send, Paperclip, Image as ImageIcon, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { MessageBubble } from "./MessageBubble";
import { MatchCard } from "./MatchCard";
import { PhotoAnalysisCard } from "./cards/PhotoAnalysisCard";
import { MedicalDocumentCard } from "./cards/MedicalDocumentCard";
import { SuccessCaseCard } from "./cards/SuccessCaseCard";
import { ApplicationAnalysis } from "./ApplicationAnalysis";
import { BehavioralAnalysis } from "./BehavioralAnalysis";
import { mockPhotoAnalysis, mockMedicalDocument, mockSuccessCases } from "@/data/mockCardData";
import { mockAnalysisData } from "@/data/mockAnalysisData";
import { mockBehavioralAnalysis } from "@/data/mockBehavioralData";
import { behavioralMatchAdopters, multiCriteriaAdopters, similaritySearchAdopters, queryInsights } from "@/data/mockAdopterData";
import { toast } from "sonner";
import { useSearch } from "@/contexts/SearchContext";
import { LiveMetricsGrid } from "./metrics/LiveMetricsGrid";
import { useSendMessage, useAnalyzeApplication } from "@/hooks/useApi";
import { ApiError } from "@/services/api";

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

interface Message {
  id: number;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  matches?: Match[];
  photoAnalysis?: typeof mockPhotoAnalysis;
  medicalDocument?: typeof mockMedicalDocument;
  successCases?: typeof mockSuccessCases;
  applicationAnalysis?: typeof mockAnalysisData;
  behavioralAnalysis?: typeof mockBehavioralAnalysis;
  attachedImage?: string;
  attachedDocument?: string;
  isProcessing?: boolean;
  searchType?: 'behavioral' | 'multiCriteria' | 'similarity';
}

const initialMessages: Message[] = [
  {
    id: 1,
    role: "assistant" as const,
    content: `Hi! I'm your AI rescue coordinator. I can help you:

• Find perfect adopter matches using semantic search
• Translate Korean medical records to English  
• Analyze dog photos to assess health/behavior
• Analyze adoption applications with Elasticsearch vector search
• Analyze foster reports and track behavioral progress
• Search through 500+ past rescue cases for guidance

Try asking:
• "Find adopters who can handle a dog with separation anxiety"
• "I need someone who works from home, has a yard, and is experienced with senior dogs"
• "Who are our best adopters similar to Emily Rodriguez?"
• Paste a foster report for behavioral analysis`,
    timestamp: new Date(),
  },
];

const mockMatches = [
  {
    name: "Sarah Chen",
    location: "Seattle, WA",
    housing: "House with yard",
    score: 92,
    highlights: [
      "Works from home (great for separation anxiety!)",
      "Previously fostered anxious dogs",
      "Patient, calm lifestyle",
    ],
    explanation: {
      semantic: 0.89,
      reason: "Semantic relevance: 0.89 (mentioned 'patient with anxious behaviors')",
      structured: "Works from home (addresses separation anxiety)",
      experience: "Successfully adopted anxious rescue in 2022",
    },
  },
  {
    name: "Michael Torres",
    location: "Portland, OR",
    housing: "House with fenced yard",
    score: 88,
    highlights: [
      "Retired teacher, home all day",
      "Experience with senior dogs",
      "Quiet neighborhood",
    ],
    explanation: {
      semantic: 0.86,
      reason: "Strong match for senior dogs with anxiety needs",
      structured: "Retired = consistent presence",
      experience: "15+ years of dog ownership",
    },
  },
];

export const ChatInterface = () => {
  const [messages, setMessages] = useState(initialMessages);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploadedFile, setUploadedFile] = useState<{ type: 'image' | 'document' | 'application', url: string } | null>(null);
  const [hasData, setHasData] = useState(false);
  const [showApplicationInput, setShowApplicationInput] = useState(false);
  const [useMockData, setUseMockData] = useState(true); // Toggle for demo mode
  const { setSearchType, setCurrentQuery, setShowTrace } = useSearch();

  // API hooks
  const sendMessage = useSendMessage();
  const analyzeApplication = useAnalyzeApplication();

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const fileUrl = URL.createObjectURL(file);
    const fileType = file.type.startsWith('image/') ? 'image' : 'document';

    setUploadedFile({ type: fileType, url: fileUrl });

    if (fileType === 'image') {
      toast.success("Photo uploaded! Send your message to analyze.");
    } else {
      toast.success("Document uploaded! Send your message to process.");
    }
  };

  // Real API handler for application analysis
  const handleRealApplicationAnalysis = async (applicationText: string) => {
    const userMessage: Message = {
      id: messages.length + 1,
      role: "user" as const,
      content: "Analyze this adoption application",
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setSearchType('applicationAnalysis');
    setCurrentQuery(applicationText);

    try {
      const result = await analyzeApplication.mutateAsync({
        application_text: applicationText,
      });

      const analysisMessage: Message = {
        id: messages.length + 2,
        role: "assistant" as const,
        content: "📊 Application Analysis Complete",
        timestamp: new Date(),
        applicationAnalysis: result.analysis,
      };
      setMessages((prev) => [...prev, analysisMessage]);
    } catch (error) {
      const errorMessage = error instanceof ApiError
        ? error.message
        : "Failed to analyze application. Please check if the backend is running.";

      toast.error(errorMessage);

      const errorMsg: Message = {
        id: messages.length + 2,
        role: "assistant" as const,
        content: `❌ Error: ${errorMessage}\n\nTip: Make sure the backend is running at http://localhost:8000`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  // Format API response - simplified version that uses Gemini's pre-formatted text
  const formatApiResponse = (response: any, intent: string): { content: string; matches?: Match[] } => {
    // If response has pre-formatted text from Gemini, use it directly
    if (response.text) {
      // Handle find_adopters intent with matches
      if (intent === "find_adopters" && response.matches) {
        const hits = response.matches;
        const matches = hits.map((hit: any) => {
          const source = hit._source || hit.data || hit;
          const score = hit._score || hit.score || 0;

          return {
            name: source.applicant_name || source.name || "Unknown Applicant",
            location: source.location || `${source.city || ''}, ${source.state || ''}`.trim() || "Not specified",
            housing: source.housing_type || "Not specified",
            score: Math.round(score >= 1 ? score * 10 : score * 100),
            highlights: source.highlights || source.key_strengths || [
              source.motivation ? `${source.motivation.substring(0, 120)}...` : null,
              source.experience_level ? `Experience: ${source.experience_level}` : null,
              source.employment_status ? `Employment: ${source.employment_status}` : null,
            ].filter(Boolean),
            explanation: {
              semantic: score,
              reason: `Match score: ${score.toFixed(3)}`,
              structured: source.housing_type || source.employment_status ?
                `Housing: ${source.housing_type || 'N/A'}, Work: ${source.employment_status || 'N/A'}` :
                "",
              experience: source.experience_level || source.previous_dog ?
                `${source.experience_level || 'Unknown'} ${source.previous_dog ? '(has dog experience)' : ''}` :
                "No experience info",
            },
          };
        });

        return {
          content: response.text,  // Use Gemini's formatted text
          matches: matches.slice(0, 10),
        };
      }

      // For other intents with text, just return the text
      return { content: response.text };
    }

    // Handle analyze_application intent
    if (intent === "analyze_application") {
      return {
        content: "📊 Application analysis complete! See the detailed breakdown below.",
      };
    }

    // Handle general string responses
    if (typeof response === "string") {
      return { content: response };
    }

    // Handle structured responses with message field
    if (response.message || response.answer) {
      return { content: response.message || response.answer };
    }

    // Fallback: show formatted JSON
    return {
      content: `📋 **Response**:\n\n\`\`\`json\n${JSON.stringify(response, null, 2)}\n\`\`\``
    };
  };

  // Real API handler for chat messages
  const handleRealChatMessage = async (message: string) => {
    const userMessage: Message = {
      id: messages.length + 1,
      role: "user" as const,
      content: message,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const result = await sendMessage.mutateAsync({
        message: message,
        context: {},
      });

      // Format the response based on intent
      const formatted = formatApiResponse(result.response, result.intent);

      const aiMessage: Message = {
        id: messages.length + 2,
        role: "assistant" as const,
        content: formatted.content,
        timestamp: new Date(),
        matches: formatted.matches,
      };
      setMessages((prev) => [...prev, aiMessage]);

      // Show intent for debugging (optional)
      if (result.intent !== "general") {
        toast.success(`Intent: ${result.intent}`);
      }
    } catch (error) {
      const errorMessage = error instanceof ApiError
        ? error.message
        : "Failed to send message. Please check if the backend is running.";

      toast.error(errorMessage);

      const errorMsg: Message = {
        id: messages.length + 2,
        role: "assistant" as const,
        content: `❌ Error: ${errorMessage}\n\nTip: Make sure the backend is running at http://localhost:8000`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSend = () => {
    if (!input.trim() && !uploadedFile) return;

    const lowerInput = input.toLowerCase();

    // Route to real API if not using mock data
    if (!useMockData) {
      // Handle application analysis with real API
      if (uploadedFile?.type === 'application' && uploadedFile.url) {
        handleRealApplicationAnalysis(uploadedFile.url);
        setInput("");
        setUploadedFile(null);
        setShowApplicationInput(false);
        return;
      }

      // Handle general chat with real API
      if (input.trim()) {
        handleRealChatMessage(input);
        setInput("");
        return;
      }
    }
    
    // Check for foster report analysis
    if ((lowerInput.includes('foster report') || lowerInput.includes('foster update')) ||
        (lowerInput.includes('week') && (lowerInput.includes('luna') || lowerInput.includes('hiding') || lowerInput.includes('tail wag')))) {
      
      const userMessage: Message = {
        id: messages.length + 1,
        role: "user" as const,
        content: input,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMessage]);
      setInput("");
      setIsLoading(true);
      setSearchType('behavioralAnalysis');
      setCurrentQuery(input);
      setShowTrace(true);

      // Simulate processing
      setTimeout(() => {
        const processingMessage: Message = {
          id: messages.length + 2,
          role: "assistant" as const,
          content: `⏳ Analyzing foster report...

✓ Extracting behavioral patterns (Gemini)
✓ Generating semantic embeddings (text-embedding-004)
✓ Elasticsearch vector search on 156 past foster reports
✓ Finding similar behavioral cases
✓ Analyzing progress patterns`,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, processingMessage]);

        // Show results
        setTimeout(() => {
          const analysisMessage: Message = {
            id: messages.length + 3,
            role: "assistant" as const,
            content: `📝 Behavioral Analysis Complete

I've analyzed Luna's Week 3 foster report and compared it to similar cases in our database. The analysis shows positive progress with typical anxiety triggers for a rescue at this stage.

Based on Elasticsearch analysis of 8 similar cases, Luna is on track for adoption readiness in 5-7 weeks with an 89% success rate.`,
            timestamp: new Date(),
            behavioralAnalysis: mockBehavioralAnalysis,
          };
          setMessages((prev) => [...prev, analysisMessage]);
          setIsLoading(false);
        }, 2000);
      }, 500);
      
      return;
    }
    
    // Check for behavioral matching query
    if ((lowerInput.includes('separation anxiety') || 
         lowerInput.includes('anxious') || 
         lowerInput.includes('anxiety')) && 
        (lowerInput.includes('adopter') || lowerInput.includes('handle') || lowerInput.includes('find'))) {
      
      const userMessage: Message = {
        id: messages.length + 1,
        role: "user" as const,
        content: input,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMessage]);
      setInput("");
      setIsLoading(true);
      setSearchType('behavioral');
      setCurrentQuery(input);
      setShowTrace(true);

      setTimeout(() => {
        const aiMessage: Message = {
          id: messages.length + 2,
          role: "assistant" as const,
          content: `Searching for adopters with separation anxiety experience...

Using Elasticsearch hybrid search:
• Semantic: "separation anxiety", "works from home", "patient"
• Structured: employment_status, previous_experience
• Ranked by: success rate with anxious dogs

Found ${behavioralMatchAdopters.length} qualified adopters:`,
          timestamp: new Date(),
          matches: behavioralMatchAdopters,
          searchType: 'behavioral',
        };
        setMessages((prev) => [...prev, aiMessage]);
        
        setTimeout(() => {
          const summaryMessage: Message = {
            id: messages.length + 3,
            role: "assistant" as const,
            content: `All ${behavioralMatchAdopters.length} have track records with anxious dogs - Elasticsearch shows 91% success rate with this group.`,
            timestamp: new Date(),
          };
          setMessages((prev) => [...prev, summaryMessage]);
          setIsLoading(false);
        }, 800);
      }, 1000);
      return;
    }

    // Check for multi-criteria search
    if ((lowerInput.includes('work from home') || lowerInput.includes('wfh')) && 
        lowerInput.includes('yard') && 
        (lowerInput.includes('senior') || lowerInput.includes('medical'))) {
      
      const userMessage: Message = {
        id: messages.length + 1,
        role: "user" as const,
        content: input,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMessage]);
      setInput("");
      setIsLoading(true);
      setSearchType('multiCriteria');
      setCurrentQuery(input);
      setShowTrace(true);

      setTimeout(() => {
        const aiMessage: Message = {
          id: messages.length + 2,
          role: "assistant" as const,
          content: `Breaking down your requirements...

Elasticsearch Query Construction:
✓ Semantic: "experienced", "medical needs", "senior"
✓ Structured:
  • employment_status = "remote"
  • housing_type = "house"
  • has_yard = true
  • senior_experience = true

Found ${multiCriteriaAdopters.length} perfect matches:`,
          timestamp: new Date(),
          matches: multiCriteriaAdopters,
          searchType: 'multiCriteria',
        };
        setMessages((prev) => [...prev, aiMessage]);
        setIsLoading(false);
      }, 1200);
      return;
    }

    // Check for similarity search
    if ((lowerInput.includes('similar') || lowerInput.includes('like')) && 
        (lowerInput.includes('emily') || lowerInput.includes('adopter'))) {
      
      const userMessage: Message = {
        id: messages.length + 1,
        role: "user" as const,
        content: input,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMessage]);
      setInput("");
      setIsLoading(true);
      setSearchType('similarity');
      setCurrentQuery(input);
      setShowTrace(true);

      setTimeout(() => {
        const aiMessage: Message = {
          id: messages.length + 2,
          role: "assistant" as const,
          content: `Finding adopters similar to Emily Rodriguez...

Using Elasticsearch vector search on Emily's profile:
• Application text embedding
• Adoption outcome: successful
• Dog type: anxious senior

Found ${similaritySearchAdopters.length} adopters with similar profiles:`,
          timestamp: new Date(),
          matches: similaritySearchAdopters,
          searchType: 'similarity',
        };
        setMessages((prev) => [...prev, aiMessage]);
        
        setTimeout(() => {
          const summaryMessage: Message = {
            id: messages.length + 3,
            role: "assistant" as const,
            content: `All ${similaritySearchAdopters.length} have successful adoptions with similar dog types. This profile has a 94% success rate.`,
            timestamp: new Date(),
          };
          setMessages((prev) => [...prev, summaryMessage]);
          setIsLoading(false);
        }, 800);
      }, 1000);
      return;
    }

    // Check if user wants to analyze an application
    if (lowerInput.includes('analyz') && lowerInput.includes('application') && !uploadedFile) {
      const userMessage: Message = {
        id: messages.length + 1,
        role: "user" as const,
        content: input,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMessage]);
      setInput("");
      setShowApplicationInput(true);
      
      setTimeout(() => {
        const aiMessage: Message = {
          id: messages.length + 2,
          role: "assistant" as const,
          content: "Great! Please paste the adoption application text in the box below and I'll analyze it using Elasticsearch vector search to find similar successful adopters.",
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, aiMessage]);
      }, 500);
      return;
    }

    const userMessage: Message = {
      id: messages.length + 1,
      role: "user" as const,
      content: input || (uploadedFile?.type === 'image' ? 'Analyze this photo' : uploadedFile?.type === 'application' ? 'Analyze this application' : 'Process this medical document'),
      timestamp: new Date(),
      attachedImage: uploadedFile?.type === 'image' ? uploadedFile.url : undefined,
      attachedDocument: uploadedFile?.type === 'document' ? uploadedFile.url : undefined,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    const currentUpload = uploadedFile;
    setUploadedFile(null);
    setIsLoading(true);
    setShowApplicationInput(false);

    // Simulate AI response based on upload type or command
    if (currentUpload?.type === 'application') {
      // Application analysis
      setTimeout(() => {
        const processingMessage: Message = {
          id: messages.length + 2,
          role: "assistant" as const,
          content: `⏳ Analyzing application...

✓ Extracting key information (Gemini)
✓ Generating semantic embeddings (text-embedding-004)
✓ Elasticsearch vector search on 203 past applications
✓ Finding similar adopter profiles
✓ Analyzing success patterns`,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, processingMessage]);

        setTimeout(() => {
          const analysisMessage: Message = {
            id: messages.length + 3,
            role: "assistant" as const,
            content: "📊 Application Analysis Complete",
            timestamp: new Date(),
            applicationAnalysis: mockAnalysisData,
          };
          setMessages((prev) => [...prev, analysisMessage]);
          setIsLoading(false);
        }, 2000);
      }, 500);
    } else if (currentUpload?.type === 'image') {
      // Photo analysis response
      setTimeout(() => {
        const aiMessage: Message = {
          id: messages.length + 2,
          role: "assistant" as const,
          content: `I analyzed the photo of this dog:\n\n🔍 AI Analysis:`,
          timestamp: new Date(),
          photoAnalysis: mockPhotoAnalysis,
        };
        setMessages((prev) => [...prev, aiMessage]);
        setIsLoading(false);

        // After 2 seconds, show search for adopters
        setTimeout(() => {
          const followUpMessage: Message = {
            id: messages.length + 3,
            role: "assistant" as const,
            content: `Based on the analysis, I'm searching for adopters who prefer senior golden retrievers with calm temperaments...`,
            timestamp: new Date(),
            matches: mockMatches.slice(0, 2),
          };
          setMessages((prev) => [...prev, followUpMessage]);
        }, 2000);
      }, 1500);
    } else if (currentUpload?.type === 'document') {
      // Medical document processing
      // Step 1: Show processing card
      setTimeout(() => {
        const processingMessage: Message = {
          id: messages.length + 2,
          role: "assistant" as const,
          content: `I've received Luna's Korean veterinary record. Processing now...`,
          timestamp: new Date(),
          medicalDocument: {
            ...mockMedicalDocument,
            processingSteps: {
              ocrComplete: false,
              translationComplete: false,
              conditionsIdentified: false,
              casesSearched: false,
            }
          },
          isProcessing: true,
        };
        setMessages((prev) => [...prev, processingMessage]);

        // Simulate step-by-step processing
        let currentStep = 0;
        const processingInterval = setInterval(() => {
          currentStep++;
          setMessages((prev) => {
            const updated = [...prev];
            const lastMsg = updated[updated.length - 1];
            if (lastMsg.medicalDocument) {
              const steps = { ...lastMsg.medicalDocument.processingSteps };
              if (currentStep === 1) steps.ocrComplete = true;
              if (currentStep === 2) steps.translationComplete = true;
              if (currentStep === 3) steps.conditionsIdentified = true;
              if (currentStep === 4) steps.casesSearched = true;
              
              lastMsg.medicalDocument = {
                ...lastMsg.medicalDocument,
                processingSteps: steps
              };
              
              if (currentStep === 4) {
                lastMsg.isProcessing = false;
                clearInterval(processingInterval);
              }
            }
            return updated;
          });
        }, 800);

        // After processing, show success cases
        setTimeout(() => {
          const successMessage: Message = {
            id: messages.length + 3,
            role: "assistant" as const,
            content: `Good news! I found dogs with similar medical conditions who were successfully adopted:\n\n📊 Pattern Analysis - What These Success Stories Tell Us:\n\nCommon Adopter Traits:\n• 🏠 Work from home or retired (73% of cases)\n• 💰 Financial stability for medical costs (100% required)\n• 🎓 Previous experience with medical-needs dogs (81%)\n• ⏰ Patient personality, long-term mindset (100%)\n• 🏥 Some medical knowledge helpful (not required)\n\n✨ Luna's chances: Excellent! Her friendly temperament + young age (estimated 3 years) make her highly adoptable with the right match.\n\nSuccess Rate Data:\n• Dogs with heartworm + malnutrition: 89% adoption success rate\n• Average time to adoption: 4.3 months (during/after treatment)`,
            timestamp: new Date(),
            successCases: mockSuccessCases,
          };
          setMessages((prev) => [...prev, successMessage]);
        }, 4500);

        setIsLoading(false);
      }, 1500);
    } else {
      // Regular text response
      setTimeout(() => {
        const aiMessage: Message = {
          id: messages.length + 2,
          role: "assistant" as const,
          content: `I found 8 applications that match well. Here are the top 3:`,
          timestamp: new Date(),
          matches: mockMatches.slice(0, 2),
        };
        setMessages((prev) => [...prev, aiMessage]);
        setIsLoading(false);
      }, 1500);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* API Mode Toggle */}
      <div className="px-6 pt-4 pb-2 border-b border-border">
        <div className="flex items-center justify-between max-w-4xl mx-auto">
          <div className="flex items-center gap-3">
            <span className="text-sm font-medium text-muted-foreground">Data Mode:</span>
            <Button
              variant={useMockData ? "default" : "outline"}
              size="sm"
              onClick={() => setUseMockData(true)}
              className="h-8"
            >
              Demo Data
            </Button>
            <Button
              variant={!useMockData ? "default" : "outline"}
              size="sm"
              onClick={() => setUseMockData(false)}
              className="h-8"
            >
              Real API
            </Button>
          </div>
          <div className="text-xs text-muted-foreground">
            {useMockData ? "Using mock data for demo" : "Connected to backend API"}
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-4">
        {!hasData && messages.length === 1 && (
          <div className="flex items-center justify-center h-full">
            <div className="max-w-md w-full border border-border rounded-lg p-8 text-center space-y-6" 
                 style={{ background: 'var(--gradient-welcome)' }}>
              <div className="text-4xl mb-2">👋</div>
              <h2 className="text-2xl font-bold text-foreground">Welcome to RescueAI!</h2>
              <p className="text-muted-foreground">
                To get started, you need to upload your rescue center's data.
              </p>
              <Button
                size="lg"
                className="w-full"
                onClick={() => window.location.href = '/data-management'}
              >
                Go to Data Management
              </Button>
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <span className="w-full border-t border-border" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-card px-2 text-muted-foreground">Or try demo mode with sample data</span>
                </div>
              </div>
              <Button
                variant="outline"
                size="lg"
                className="w-full hover:bg-muted/50"
                onClick={() => setHasData(true)}
              >
                Load Demo Data
              </Button>
            </div>
          </div>
        )}
        {(hasData || messages.length > 1) && (
          <>
        {/* Live Metrics Grid - Only show when there's data */}
        {messages.length === 1 && (
          <div className="mb-6">
            <LiveMetricsGrid />
          </div>
        )}
        {messages.map((message) => (
          <div key={message.id}>
            <MessageBubble message={message} />
            {message.photoAnalysis && (
              <div className="mt-4">
                <PhotoAnalysisCard analysis={message.photoAnalysis} />
              </div>
            )}
            {message.medicalDocument && (
              <div className="mt-4">
                <MedicalDocumentCard 
                  document={message.medicalDocument} 
                  isProcessing={message.isProcessing}
                />
              </div>
            )}
            {message.successCases && (
              <div className="mt-4 space-y-3">
                {message.successCases.map((successCase, idx) => (
                  <SuccessCaseCard 
                    key={idx} 
                    successCase={successCase}
                    onViewFullCase={() => toast.info(`Opening case ${successCase.caseId}`)}
                    onSeeAdopterProfile={() => toast.info("Opening adopter profile")}
                  />
                ))}
              </div>
            )}
            {message.applicationAnalysis && (
              <div className="mt-4">
                <ApplicationAnalysis {...message.applicationAnalysis} />
              </div>
            )}
            {message.behavioralAnalysis && (
              <div className="mt-4">
                <BehavioralAnalysis data={message.behavioralAnalysis} />
              </div>
            )}
            {message.matches && (
              <div className="mt-4 space-y-3">
                {message.matches.map((match, idx) => (
                  <MatchCard key={idx} match={match} />
                ))}
              </div>
            )}
          </div>
        ))}
        {isLoading && (
          <div className="flex items-center space-x-2 text-muted-foreground">
            <div className="animate-spin rounded-full h-4 w-4 border-2 border-primary border-t-transparent"></div>
            <span className="text-sm">Analyzing with Google Cloud AI...</span>
          </div>
        )}
        </>
        )}
      </div>

      {/* Input Area */}
      <div className="p-4">
        <div className="max-w-4xl mx-auto border border-border bg-card rounded-2xl p-4 shadow-sm">
          {showApplicationInput && (
            <div className="mb-3 p-4 bg-[#CFE1B9]/10 border border-[#CFE1B9] rounded-lg">
              <div className="flex items-center mb-2">
                <FileText className="h-4 w-4 text-[#718355] mr-2" />
                <p className="text-sm font-semibold text-foreground">Paste Application Text</p>
              </div>
              <Textarea
                placeholder="Paste the adoption application here... (e.g., Why do you want to adopt? Tell us about your home and experience...)"
                className="min-h-[150px] mb-2"
                onChange={(e) => {
                  if (e.target.value.trim()) {
                    setUploadedFile({ type: 'application', url: e.target.value });
                  } else {
                    setUploadedFile(null);
                  }
                }}
              />
              <div className="flex gap-2">
                <Button 
                  onClick={() => {
                    if (uploadedFile?.type === 'application') {
                      handleSend();
                    }
                  }}
                  disabled={!uploadedFile}
                  className="flex-1 bg-secondary hover:bg-secondary/80 text-secondary-foreground"
                >
                  <Send className="h-4 w-4 mr-2" />
                  Analyze Application
                </Button>
                <Button 
                  onClick={() => {
                    setShowApplicationInput(false);
                    setUploadedFile(null);
                  }}
                  variant="outline"
                >
                  Cancel
                </Button>
              </div>
            </div>
          )}
          {uploadedFile && uploadedFile.type !== 'application' && (
            <div className="mb-3 p-3 bg-primary/10 border border-primary/30 rounded-lg flex items-center justify-between">
              <div className="flex items-center space-x-2">
                {uploadedFile.type === 'image' ? (
                  <ImageIcon className="h-4 w-4 text-primary" />
                ) : (
                  <FileText className="h-4 w-4 text-primary" />
                )}
                <span className="text-sm text-foreground">
                  {uploadedFile.type === 'image' ? 'Photo ready to analyze' : 'Document ready to process'}
                </span>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setUploadedFile(null)}
                className="h-6 text-xs"
              >
                Remove
              </Button>
            </div>
          )}
          <div className="flex items-end space-x-2">
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              accept="image/*,.pdf,.doc,.docx"
              className="hidden"
            />
            <Button 
              variant="ghost" 
              size="icon" 
              className="mb-2 hover:bg-muted/50"
              onClick={() => fileInputRef.current?.click()}
              title="Upload photo or document"
            >
              <Paperclip className="h-5 w-5 text-muted-foreground" />
            </Button>
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              placeholder={uploadedFile ? "Describe what you'd like to know..." : "Ask me anything, or upload a photo/document..."}
              className="min-h-[60px] resize-none border-border"
            />
            <Button
              onClick={handleSend}
              disabled={(!input.trim() && !uploadedFile) || isLoading}
              className="mb-2 bg-secondary hover:bg-secondary/80 text-secondary-foreground"
              size="icon"
            >
              <Send className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};
