import { useState, useRef, useEffect } from "react";
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
import { toast } from "sonner";
import { useSearch } from "@/contexts/SearchContext";
import { useSendMessage, useAnalyzeApplication, useCreateSession } from "@/hooks/useApi";
import { ApiError } from "@/services/api";

interface Match {
  name: string;
  location: string;
  housing: string;
  score: number;
  highlights: string[];
  matchReason?: string; // AI-generated reason for this specific match
  explanation: {
    semantic: number;
    reason: string;
    structured: string;
    experience: string;
  };
}

interface PhotoAnalysis {
  breed: string;
  confidence: number;
  age: string;
  healthIndicators: Array<{ label: string; status: string; icon: string }>;
  personality: string[];
  recommendations: string[];
}

interface MedicalDocument {
  originalLanguage: string;
  translatedText: string;
  conditions: string[];
  medications: string[];
  processingSteps?: {
    ocrComplete: boolean;
    translationComplete: boolean;
    conditionsIdentified: boolean;
    casesSearched: boolean;
  };
}

interface SuccessCase {
  caseId: string;
  dogName: string;
  breed: string;
  conditions: string[];
  adopter: string;
  outcome: string;
  timeToAdoption: string;
  similarity: number;
}

interface ApplicationAnalysis {
  applicantName?: string;
  strengths?: string[];
  experienceLevel?: string;
  bestSuitedFor?: string[];
  successRate?: number;
  successFactors?: Record<string, number>;
  recommendedDogs?: any[];
  similarAdopters?: any[];
}

interface BehavioralAnalysis {
  dog_name: string;
  week: number;
  progress_score: number;
  behavioral_metrics: any;
  similar_cases: any[];
  recommendations: string[];
}

interface Message {
  id: number;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  matches?: Match[];
  photoAnalysis?: PhotoAnalysis;
  medicalDocument?: MedicalDocument;
  successCases?: SuccessCase[];
  applicationAnalysis?: ApplicationAnalysis;
  behavioralAnalysis?: BehavioralAnalysis;
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

export const ChatInterface = () => {
  const [messages, setMessages] = useState(initialMessages);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploadedFile, setUploadedFile] = useState<{ type: 'image' | 'document' | 'application', url: string } | null>(null);
  const [hasData, setHasData] = useState(true);
  const [showApplicationInput, setShowApplicationInput] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null); // Track current session
  const [applicantsData, setApplicantsData] = useState<any[]>([]); // Store full applicant data for follow-up queries
  const { setSearchType, setCurrentQuery, setShowTrace, loadedSessionId, loadedMessages, setLoadedSessionId, setTraceData } = useSearch();

  // API hooks
  const sendMessage = useSendMessage();
  const analyzeApplication = useAnalyzeApplication();
  const createSession = useCreateSession();

  // Load messages from loaded session
  useEffect(() => {
    if (loadedSessionId && loadedMessages.length > 0) {
      console.log("Loading session:", loadedSessionId);
      console.log("Raw loaded messages:", loadedMessages);

      // Track if we found applicant data to restore
      let restoredApplicantsData: any[] = [];

      // Convert loaded messages to Message format
      const convertedMessages: Message[] = loadedMessages.map((msg, index) => {
        console.log(`Message ${index} metadata:`, msg.metadata);
        console.log(`Message ${index} matches:`, msg.metadata?.matches);

        // Build the message object with all potential fields
        const convertedMessage: Message = {
          id: index + 1,
          role: msg.role,
          content: msg.content,
          timestamp: new Date(msg.timestamp),
        };

        // Add metadata fields if they exist
        if (msg.metadata) {
          if (msg.metadata.matches && Array.isArray(msg.metadata.matches)) {
            // Store the raw matches data for follow-up queries
            const rawMatches = msg.metadata.matches.map((hit: any) => hit._source || hit.data || hit);
            if (rawMatches.length > 0) {
              restoredApplicantsData = rawMatches; // Keep the most recent matches
            }

            // Transform raw Elasticsearch matches into the format MatchCard expects
            const transformedMatches = msg.metadata.matches.map((hit: any) => {
              const source = hit._source || hit.data || hit;
              const score = hit._score || hit.score || 0;

              return {
                name: source.applicant_name || source.name || "Unknown Applicant",
                location: source.location || `${source.city || ''}, ${source.state || ''}`.trim() || "Not specified",
                housing: source.housing_type || "Not specified",
                score: Math.round(score >= 1 ? score * 10 : score * 100),
                matchReason: hit.match_reason || source.match_reason, // AI-generated match reason
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

            convertedMessage.matches = transformedMatches;
            console.log(`✓ Added ${transformedMatches.length} transformed matches to message ${index}`);
          }
          if (msg.metadata.photoAnalysis) {
            convertedMessage.photoAnalysis = msg.metadata.photoAnalysis;
          }
          if (msg.metadata.medicalDocument) {
            convertedMessage.medicalDocument = msg.metadata.medicalDocument;
          }
          if (msg.metadata.successCases) {
            convertedMessage.successCases = msg.metadata.successCases;
          }
          if (msg.metadata.applicationAnalysis) {
            convertedMessage.applicationAnalysis = msg.metadata.applicationAnalysis;
          }
          if (msg.metadata.behavioralAnalysis) {
            convertedMessage.behavioralAnalysis = msg.metadata.behavioralAnalysis;
          }
        }

        return convertedMessage;
      });

      console.log("Converted messages:", convertedMessages);
      setMessages(convertedMessages);
      setSessionId(loadedSessionId);

      // Restore applicants data if we found any
      if (restoredApplicantsData.length > 0) {
        setApplicantsData(restoredApplicantsData);
        console.log(`✅ Restored ${restoredApplicantsData.length} applicants from session history`);
      }

      // Clear the loaded session from context
      setLoadedSessionId(null);
    }
  }, [loadedSessionId, loadedMessages]);

  // Create new session on mount
  useEffect(() => {
    if (!sessionId && !loadedSessionId) {
      createSession.mutateAsync().then((result) => {
        setSessionId(result.session_id);
        console.log("Created new session:", result.session_id);
      }).catch((error) => {
        console.error("Failed to create session:", error);
      });
    }
  }, []);

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

      // Store trace data if available
      if (result.trace) {
        setTraceData(result.trace);
        setShowTrace(true);
      }

      // Get the formatted summary text from the backend
      const formattedSummary = result.text || "Application analysis complete";

      const analysisMessage: Message = {
        id: messages.length + 2,
        role: "assistant" as const,
        content: formattedSummary,  // Use the formatted ChatGPT-style summary
        timestamp: new Date(),
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
        content: `❌ Error: ${errorMessage}\n\nTip: Make sure the backend is running and accessible.`,
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
            matchReason: hit.match_reason || source.match_reason, // AI-generated match reason
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
      console.log("📤 Sending message with context:", {
        has_session: !!sessionId,
        applicants_count: applicantsData.length
      });

      const result = await sendMessage.mutateAsync({
        message: message,
        context: {
          ...(sessionId ? { session_id: sessionId } : {}),
          ...(applicantsData.length > 0 ? { applicants_data: applicantsData } : {}),
        },
      });

      // Update session ID if returned from backend
      if (result.session_id && result.session_id !== sessionId) {
        setSessionId(result.session_id);
      }

      // Store trace data if available
      if (result.trace) {
        setTraceData(result.trace);
        setShowTrace(true);
      }

      // Debug: Log the API response
      console.log("Full API result:", JSON.stringify(result, null, 2));
      console.log("Response.matches:", result.response?.matches);

      // Format the response based on intent
      const formatted = formatApiResponse(result.response, result.intent);
      console.log("Formatted matches:", formatted.matches);

      // Store applicants data for follow-up queries
      if (result.response?.matches && Array.isArray(result.response.matches)) {
        const fullApplicantsData = result.response.matches.map((hit: any) => hit._source || hit.data || hit);
        setApplicantsData(fullApplicantsData);
        console.log("✅ Stored", fullApplicantsData.length, "applicants for follow-up queries");
        console.log("Sample applicant names:", fullApplicantsData.slice(0, 3).map((a: any) => a.applicant_name));
      }

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
        content: `❌ Error: ${errorMessage}\n\nTip: Make sure the backend is running and accessible.`,
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
            // Demo mode - would show real behavioral analysis from API
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

Demo mode - use Real API mode for live results`,
          timestamp: new Date(),
          matches: [],
          searchType: 'behavioral',
        };
        setMessages((prev) => [...prev, aiMessage]);

        setTimeout(() => {
          const summaryMessage: Message = {
            id: messages.length + 3,
            role: "assistant" as const,
            content: `Switch to Real API mode to see live results from your Elasticsearch database.`,
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

Demo mode - use Real API mode for live results`,
          timestamp: new Date(),
          matches: [],
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

Demo mode - use Real API mode for live results`,
          timestamp: new Date(),
          matches: [],
          searchType: 'similarity',
        };
        setMessages((prev) => [...prev, aiMessage]);

        setTimeout(() => {
          const summaryMessage: Message = {
            id: messages.length + 3,
            role: "assistant" as const,
            content: `Switch to Real API mode to see live results from your Elasticsearch database.`,
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
            content: "📊 Application Analysis Complete - Demo mode. Use Real API mode for live analysis.",
            timestamp: new Date(),
            // Demo mode - would show real analysis from API
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
          content: `Photo analysis - Demo mode. Use Real API mode for live photo analysis with Google Cloud Vision API.`,
          timestamp: new Date(),
          // Demo mode - would show real photo analysis from API
        };
        setMessages((prev) => [...prev, aiMessage]);
        setIsLoading(false);

        // Demo mode - no follow-up in demo mode
      }, 1500);
    } else if (currentUpload?.type === 'document') {
      // Medical document processing
      // Step 1: Show processing card
      setTimeout(() => {
        const processingMessage: Message = {
          id: messages.length + 2,
          role: "assistant" as const,
          content: `Medical document processing - Demo mode. Use Real API mode for live OCR and translation.`,
          timestamp: new Date(),
          medicalDocument: {
            originalLanguage: "Korean",
            translatedText: "Demo mode",
            conditions: [],
            medications: [],
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
            content: `Demo mode - Use Real API mode to search historical success cases in your database.`,
            timestamp: new Date(),
            successCases: [],
          };
          setMessages((prev) => [...prev, successMessage]);
        }, 4500);

        setIsLoading(false);
      }, 1500);
    } else {
      // Regular text response - Demo mode
      setTimeout(() => {
        const aiMessage: Message = {
          id: messages.length + 2,
          role: "assistant" as const,
          content: `Demo mode - Switch to Real API mode to search your adopter database.`,
          timestamp: new Date(),
          matches: [],
        };
        setMessages((prev) => [...prev, aiMessage]);
        setIsLoading(false);
      }, 1500);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto custom-scrollbar px-6 py-6 space-y-4">
        {!hasData && messages.length === 1 && (
          <div className="flex items-center justify-center h-full">
            <div className="max-w-md w-full border border-border rounded-lg p-8 text-center space-y-6"
              style={{ background: 'var(--gradient-welcome)' }}>
              <div className="text-4xl mb-2">👋</div>
              <h2 className="text-2xl font-bold text-foreground">Welcome to PawBondAI!</h2>
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
                    {message.matches.length > 0 && applicantsData.length > 0 && (
                      <div className="mt-4 p-4 bg-secondary/10 rounded-lg border border-secondary/30">
                        <p className="text-sm text-muted-foreground mb-3">
                          💡 Want to learn more? Ask me about any specific applicant by name!
                        </p>
                        <div className="text-xs text-muted-foreground">
                          Example: "Tell me more about {message.matches[0]?.name}"
                        </div>
                      </div>
                    )}
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
