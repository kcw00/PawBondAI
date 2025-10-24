import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { 
  ChevronLeft, ChevronRight, MapPin, Edit, Upload, FileText, 
  Calendar, AlertTriangle, Plus, Search, Mail, Archive, Share2,
  CheckCircle, Clock, XCircle
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";

// Mock data for Luna - Internal Staff View
const mockDogData = {
  id: "luna",
  internalId: "dog_luna_20240915",
  name: "Luna",
  breed: "Korean Jindo Mix",
  age: "~3 years (estimated)",
  size: "Medium (45 lbs)",
  gender: "Female, spayed",
  location: "Seoul Rescue Center",
  intakeDate: "September 15, 2024",
  daysInRescue: 31,
  status: "Available for Adoption",
  photos: [
    { url: "https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=800", isPublic: true, type: "general" },
    { url: "https://images.unsplash.com/photo-1568572933382-74d440642117?w=800", isPublic: true, type: "general" },
    { url: "https://images.unsplash.com/photo-1548199973-03cce0bbc87b?w=800", isPublic: true, type: "general" },
    { url: "https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?w=800", isPublic: false, type: "medical" },
    { url: "https://images.unsplash.com/photo-1477884213360-7e9d7dcc1e48?w=800", isPublic: false, type: "intake" }
  ],
  personality: {
    traits: [
      { name: "Gentle", variant: "default" as const },
      { name: "Shy", variant: "secondary" as const },
      { name: "Anxious", variant: "secondary" as const },
      { name: "Smart", variant: "default" as const },
      { name: "Loyal", variant: "default" as const }
    ],
    staffNotes: `Luna takes 2-3 weeks to warm up to new people. Recommend experienced adopters only. Keep away from loud/chaotic environments.

Update 10/12: Showing improvement with volunteer Sarah - bonds well with patient handlers.`,
    behavioralTesting: {
      kids: { result: "⚠️ Older kids (10+) only", status: "caution" },
      dogs: { result: "✅ Calm dogs only", status: "good" },
      cats: { result: "❓ Unknown", status: "unknown" },
      separationAnxiety: { result: "🔴 High", status: "concern" },
      leashManners: { result: "🟢 Excellent", status: "good" }
    },
    energyLevel: 2
  },
  rescueHistory: {
    found: {
      date: "September 8, 2024",
      location: "Streets of Seoul, Gangnam district",
      condition: "Critical - starving, scared",
      rescuedBy: "Volunteer Kim Min-ji"
    },
    intake: {
      date: "September 10, 2024",
      notes: "Initial vet exam - heartworm diagnosed"
    }
  },
  staffNotesHistory: [
    {
      date: "Oct 15",
      author: "Coordinator Sarah",
      note: "Luna showed great progress with new volunteer handler. Wagging tail today! Ready to start showing to adopters."
    },
    {
      date: "Oct 12",
      author: "Vet Dr. Lee",
      note: "Treatment progressing well. Weight gain on track. Cleared for adoption with continued treatment protocol."
    },
    {
      date: "Oct 8",
      author: "Volunteer Mike",
      note: "Luna responded well to slow approach. Took treats from hand after 20 minutes. Building trust."
    }
  ],
  statusChangeLog: [
    { date: "Oct 15", from: "Medical Hold", to: "Available", changedBy: "Dr. Lee" },
    { date: "Sept 15", from: "Intake", to: "Medical Hold", changedBy: "Coordinator Sarah" },
    { date: "Sept 10", from: null, to: "Intake", changedBy: "Admin" }
  ],
  medical: {
    conditions: [
      { 
        name: "Heartworm positive (Class 2)", 
        severity: "high",
        diagnosis: "Sept 10, 2024",
        treatmentStarted: "Sept 15, 2024",
        expectedCompletion: "March 2025",
        costToDate: "$450",
        remainingCost: "$750"
      },
      { 
        name: "Malnutrition (recovering)", 
        severity: "medium",
        initialWeight: "35 lbs (critical)",
        currentWeight: "42 lbs (improving)",
        targetWeight: "45-48 lbs"
      }
    ],
    medications: [
      { name: "Ivermectin", frequency: "monthly", nextDose: "Oct 20" },
      { name: "Doxycycline", frequency: "daily", remaining: "4 months" },
      { name: "Iron supplement", frequency: "daily", remaining: "ongoing" }
    ],
    timeline: [
      {
        date: "Oct 2024",
        title: "Treatment Update",
        description: "Monthly check-up completed, responding well",
        current: true
      },
      {
        date: "Sept 15, 2024",
        title: "Treatment Started",
        description: "Heartworm protocol initiated",
        current: false
      },
      {
        date: "Sept 10, 2024",
        title: "Initial Diagnosis",
        description: "Heartworm positive, severe malnutrition",
        current: false
      }
    ],
    documents: [
      { name: "korean_vet_exam_sept10.pdf", shareable: true },
      { name: "heartworm_treatment_plan.pdf", shareable: true },
      { name: "xray_chest_sept15.jpg", shareable: false, internal: true },
      { name: "blood_test_results_oct1.pdf", shareable: true },
      { name: "intake_photos.zip", shareable: false, internal: true }
    ]
  },
  matching: {
    requirements: [
      "Has experience with anxious dogs",
      "Works from home or retired",
      "Can commit to 6-month medical treatment",
      "Budget for $80/month medical costs",
      "Quiet household, no young kids"
    ],
    matches: [
      {
        id: 1,
        name: "Sarah Chen",
        location: "Seattle, WA",
        matchScore: 92,
        reasons: [
          "Works from home",
          "Experienced with anxious rescues",
          "Financial stability",
          "Previous senior dog adopter"
        ],
        concerns: ["Lives 50 miles from center"],
        status: "contacted"
      },
      {
        id: 2,
        name: "Michael Rodriguez",
        location: "Portland, OR",
        matchScore: 88,
        reasons: [
          "Retired, home all day",
          "Previous medical needs dog",
          "Quiet household",
          "Strong references"
        ],
        concerns: ["First time with anxious dog"],
        status: "pending"
      }
    ],
    communications: [
      { date: "Oct 15", action: "Sent Luna's profile to Sarah Chen" },
      { date: "Oct 14", action: "Sarah responded - very interested" },
      { date: "Oct 13", action: "Scheduled meet-and-greet" }
    ]
  },
  adoption: {
    requirements: [
      "Experience with anxious/fearful dogs required",
      "Commitment to 6-month heartworm treatment",
      "Budget for medical costs (~$80/month)",
      "Quiet, patient household environment",
      "Work from home or retired (for anxiety support)"
    ],
    fee: 200,
    successRate: 89
  }
};

const DogProfilePage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [currentPhotoIndex, setCurrentPhotoIndex] = useState(0);
  const [status, setStatus] = useState(mockDogData.status);
  const [newNote, setNewNote] = useState("");

  const dog = mockDogData;

  const nextPhoto = () => {
    setCurrentPhotoIndex((prev) => (prev + 1) % dog.photos.length);
  };

  const prevPhoto = () => {
    setCurrentPhotoIndex((prev) => (prev - 1 + dog.photos.length) % dog.photos.length);
  };

  const getStatusColor = (currentStatus: string) => {
    if (currentStatus.includes("Available")) return "bg-success/20 text-success border-success/30";
    if (currentStatus.includes("Adopted")) return "bg-primary/20 text-primary border-primary/30";
    if (currentStatus.includes("Medical Hold")) return "bg-warning/20 text-warning border-warning/30";
    return "bg-muted text-muted-foreground border-border";
  };

  const getStatusIcon = (currentStatus: string) => {
    if (currentStatus.includes("Available")) return "🟢";
    if (currentStatus.includes("Adopted")) return "✅";
    if (currentStatus.includes("Medical Hold")) return "🟡";
    if (currentStatus.includes("Foster")) return "🔵";
    return "⚪";
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Admin Header */}
      <div className="border-b border-border bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between mb-4">
            <Button variant="ghost" onClick={() => navigate(-1)}>
              <ChevronLeft className="w-4 h-4 mr-2" />
              Back to Dogs
            </Button>
            <Button variant="outline">
              <Edit className="w-4 h-4 mr-2" />
              Edit Profile
            </Button>
          </div>

          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h1 className="text-3xl font-bold text-foreground mb-1">
                {dog.name} • {dog.breed} • {dog.age}
              </h1>
              <p className="text-sm text-muted-foreground mb-3">Internal ID: {dog.internalId}</p>
              
              <div className="flex items-center gap-4 mb-4">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">Status:</span>
                  <Select value={status} onValueChange={setStatus}>
                    <SelectTrigger className="w-[200px]">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Available for Adoption">🟢 Available for Adoption</SelectItem>
                      <SelectItem value="Foster">🔵 Foster</SelectItem>
                      <SelectItem value="Medical Hold">🟡 Medical Hold</SelectItem>
                      <SelectItem value="Adopted">✅ Adopted</SelectItem>
                      <SelectItem value="Deceased">⚫ Deceased</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="flex flex-wrap gap-2">
                <Button size="sm" className="bg-primary hover:bg-primary/90">
                  <Search className="w-4 h-4 mr-2" />
                  Find Matches
                </Button>
                <Button size="sm" variant="outline">
                  <FileText className="w-4 h-4 mr-2" />
                  View Applications
                </Button>
                <Button size="sm" variant="outline">
                  <Plus className="w-4 h-4 mr-2" />
                  Add Medical Note
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Photo Gallery */}
      <div className="container mx-auto px-4 py-6">
        <Card>
          <CardContent className="p-6">
            <div className="relative aspect-[16/9] rounded-lg overflow-hidden bg-muted mb-4">
              <img
                src={dog.photos[currentPhotoIndex].url}
                alt={`${dog.name} photo ${currentPhotoIndex + 1}`}
                className="w-full h-full object-cover"
              />
              
              {dog.photos.length > 1 && (
                <>
                  <Button
                    variant="secondary"
                    size="icon"
                    className="absolute left-2 top-1/2 -translate-y-1/2 rounded-full shadow-lg"
                    onClick={prevPhoto}
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="secondary"
                    size="icon"
                    className="absolute right-2 top-1/2 -translate-y-1/2 rounded-full shadow-lg"
                    onClick={nextPhoto}
                  >
                    <ChevronRight className="w-4 h-4" />
                  </Button>
                </>
              )}

              <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-2">
                {dog.photos.map((_, index) => (
                  <button
                    key={index}
                    onClick={() => setCurrentPhotoIndex(index)}
                    className={`w-2 h-2 rounded-full transition-all ${
                      index === currentPhotoIndex ? "bg-white w-8" : "bg-white/50"
                    }`}
                  />
                ))}
              </div>
            </div>

            <div className="flex gap-2 mb-2">
              <Button size="sm" variant="outline">
                <Upload className="w-4 h-4 mr-2" />
                Upload More Photos
              </Button>
              <Button size="sm" variant="outline">Set as Primary</Button>
            </div>

            <div className="text-sm text-muted-foreground">
              📸 Photos for public sharing: {dog.photos.filter(p => p.isPublic).length} selected
              <br />
              📸 Internal only photos: {dog.photos.filter(p => !p.isPublic).length} (medical, intake)
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content - Tabs */}
      <div className="container mx-auto px-4 pb-32">
        <Tabs defaultValue="info" className="w-full">
          <TabsList className="grid w-full grid-cols-4 max-w-3xl mx-auto">
            <TabsTrigger value="info">Dog Information</TabsTrigger>
            <TabsTrigger value="medical">Medical Records</TabsTrigger>
            <TabsTrigger value="matching">Matching</TabsTrigger>
            <TabsTrigger value="history">History & Notes</TabsTrigger>
          </TabsList>

          {/* Tab 1: Dog Information */}
          <TabsContent value="info" className="mt-6 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>📋 Basic Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Name</p>
                    <p className="font-semibold">{dog.name}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Breed</p>
                    <p className="font-semibold">{dog.breed}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Age</p>
                    <p className="font-semibold">{dog.age}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Size</p>
                    <p className="font-semibold">{dog.size}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Gender</p>
                    <p className="font-semibold">{dog.gender}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Current Location</p>
                    <p className="font-semibold">{dog.location}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Intake Date</p>
                    <p className="font-semibold">{dog.intakeDate}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Days in Rescue</p>
                    <p className="font-semibold">{dog.daysInRescue} days</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>🐕 Personality & Behavior</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <h3 className="font-semibold mb-3">Official Assessment:</h3>
                  <div className="flex flex-wrap gap-2">
                    {dog.personality.traits.map((trait, index) => (
                      <Badge key={index} variant={trait.variant}>
                        {trait.name}
                      </Badge>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="font-semibold mb-3">Internal Staff Notes:</h3>
                  <div className="bg-muted p-4 rounded-lg">
                    <p className="text-sm whitespace-pre-line">{dog.personality.staffNotes}</p>
                  </div>
                  <div className="flex gap-2 mt-3">
                    <Button size="sm" variant="outline">
                      <Plus className="w-4 h-4 mr-2" />
                      Add Note
                    </Button>
                    <Button size="sm" variant="outline">
                      <Edit className="w-4 h-4 mr-2" />
                      Edit Assessment
                    </Button>
                  </div>
                </div>

                <div>
                  <h3 className="font-semibold mb-3">Behavioral Testing Results:</h3>
                  <div className="space-y-2">
                    {Object.entries(dog.personality.behavioralTesting).map(([key, value]) => (
                      <div key={key} className="flex items-center justify-between p-2 bg-muted rounded">
                        <span className="text-sm capitalize">{key.replace(/([A-Z])/g, ' $1').trim()}:</span>
                        <span className="text-sm font-semibold">{value.result}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="font-semibold mb-3">Energy Level:</h3>
                  <div className="flex items-center gap-2">
                    {[1, 2, 3, 4, 5].map((level) => (
                      <span
                        key={level}
                        className={`text-2xl ${
                          level <= dog.personality.energyLevel ? "text-warning" : "text-muted"
                        }`}
                      >
                        ⭐
                      </span>
                    ))}
                    <span className="ml-2 text-muted-foreground">
                      ({dog.personality.energyLevel}/5)
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Tab 2: Medical Records (SENSITIVE) */}
          <TabsContent value="medical" className="mt-6">
            <Card className="border-warning">
              <CardHeader className="bg-warning/10">
                <CardTitle className="flex items-center gap-2 text-warning">
                  <AlertTriangle className="w-5 h-5" />
                  🏥 Complete Medical History - STAFF ONLY
                </CardTitle>
                <p className="text-sm text-muted-foreground mt-2">
                  ⚠️ Do not share raw medical data with adopters without vet approval
                </p>
              </CardHeader>
              <CardContent className="space-y-6 mt-6">
                <div>
                  <h3 className="font-semibold mb-3 text-red-600 flex items-center gap-2">
                    <XCircle className="w-4 h-4" />
                    Active Medical Conditions:
                  </h3>
                  {dog.medical.conditions.map((condition, index) => (
                    <div key={index} className="mb-4 p-4 bg-muted rounded-lg">
                      <div className="flex items-start gap-2 mb-2">
                        <span className={condition.severity === "high" ? "text-red-500" : "text-amber-500"}>
                          {condition.severity === "high" ? "🔴" : "🟡"}
                        </span>
                        <div className="flex-1">
                          <p className="font-semibold">{condition.name}</p>
                          {condition.diagnosis && (
                            <div className="text-sm text-muted-foreground mt-2 space-y-1">
                              <p>Diagnosis: {condition.diagnosis}</p>
                              {condition.treatmentStarted && <p>Treatment started: {condition.treatmentStarted}</p>}
                              {condition.expectedCompletion && <p>Expected completion: {condition.expectedCompletion}</p>}
                              {condition.costToDate && <p>Cost to date: {condition.costToDate}</p>}
                              {condition.remainingCost && <p>Remaining cost estimate: {condition.remainingCost}</p>}
                            </div>
                          )}
                          {condition.initialWeight && (
                            <div className="text-sm text-muted-foreground mt-2 space-y-1">
                              <p>Initial weight: {condition.initialWeight}</p>
                              <p>Current weight: {condition.currentWeight}</p>
                              <p>Target weight: {condition.targetWeight}</p>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                <div>
                  <h3 className="font-semibold mb-3">💊 Current Medications:</h3>
                  <div className="space-y-2">
                    {dog.medical.medications.map((med, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-muted rounded">
                        <div>
                          <p className="font-medium">{med.name}</p>
                          <p className="text-sm text-muted-foreground">{med.frequency}</p>
                        </div>
                        {med.nextDose && (
                          <Badge variant="outline">Next: {med.nextDose}</Badge>
                        )}
                        {med.remaining && (
                          <Badge variant="outline">{med.remaining}</Badge>
                        )}
                      </div>
                    ))}
                  </div>
                  <div className="flex gap-2 mt-3">
                    <Button size="sm" variant="outline">
                      <Clock className="w-4 h-4 mr-2" />
                      Set Reminder
                    </Button>
                    <Button size="sm" variant="outline">
                      <CheckCircle className="w-4 h-4 mr-2" />
                      Record Dose
                    </Button>
                  </div>
                </div>

                <div>
                  <h3 className="font-semibold mb-4">📅 Treatment Timeline:</h3>
                  <div className="space-y-4 ml-4">
                    {dog.medical.timeline.map((event, index) => (
                      <div key={index} className="relative pl-6 pb-4 border-l-2 border-primary/20 last:border-0">
                        <div
                          className={`absolute left-[-9px] w-4 h-4 rounded-full ${
                            event.current
                              ? "bg-primary ring-4 ring-primary/20"
                              : "bg-muted border-2 border-primary/30"
                          }`}
                        />
                        <div className="space-y-1">
                          <p className="text-sm text-muted-foreground">
                            {event.date} {event.current && <Badge variant="secondary" className="ml-2">Current</Badge>}
                          </p>
                          <p className="font-semibold">{event.title}</p>
                          <p className="text-sm text-muted-foreground">{event.description}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="font-semibold mb-3">📄 Medical Documents ({dog.medical.documents.length}):</h3>
                  <div className="space-y-2">
                    {dog.medical.documents.map((doc, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-muted rounded">
                        <div className="flex items-center gap-2">
                          <FileText className="w-4 h-4" />
                          <span className="text-sm">{doc.name}</span>
                          {doc.internal && (
                            <Badge variant="destructive" className="text-xs">Internal Only</Badge>
                          )}
                        </div>
                        <div className="flex gap-2">
                          <Button size="sm" variant="link">View</Button>
                          {doc.shareable && (
                            <Button size="sm" variant="link">Share with Adopter?</Button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                  <Button size="sm" variant="outline" className="mt-3">
                    <Upload className="w-4 h-4 mr-2" />
                    Upload New Document
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Tab 3: Matching & Applications */}
          <TabsContent value="matching" className="mt-6">
            <Card>
              <CardHeader>
                <CardTitle>🎯 Find Perfect Adopters</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <h3 className="font-semibold mb-3">{dog.name} needs an adopter who:</h3>
                  <ul className="space-y-2">
                    {dog.matching.requirements.map((req, index) => (
                      <li key={index} className="flex items-start gap-2">
                        <span className="text-success mt-1">✓</span>
                        <span>{req}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <Button className="w-full">
                  <Search className="w-4 h-4 mr-2" />
                  Search All Applications (Triggers AI)
                </Button>

                <div>
                  <h3 className="font-semibold mb-4">
                    📊 AI Recommendations ({dog.matching.matches.length} matches found):
                  </h3>
                  <div className="space-y-4">
                    {dog.matching.matches.map((match) => (
                      <Card key={match.id} className="border-2 border-success/30">
                        <CardContent className="p-4">
                          <div className="flex items-start justify-between mb-3">
                            <div>
                              <h4 className="font-bold text-lg">{match.name}</h4>
                              <p className="text-sm text-muted-foreground flex items-center gap-1">
                                <MapPin className="w-3 h-3" />
                                {match.location}
                              </p>
                            </div>
                            <Badge className="bg-success/20 text-success border-success/30">
                              {match.matchScore}% Match 🟢
                            </Badge>
                          </div>

                          <div className="space-y-3">
                            <div>
                              <p className="text-sm font-semibold mb-2">Why good match:</p>
                              <ul className="space-y-1">
                                {match.reasons.map((reason, idx) => (
                                  <li key={idx} className="text-sm flex items-start gap-2">
                                    <span className="text-success">✓</span>
                                    <span>{reason}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>

                            {match.concerns.length > 0 && (
                              <div>
                                <p className="text-sm font-semibold mb-2 text-warning">⚠️ Consider:</p>
                                <ul className="space-y-1">
                                  {match.concerns.map((concern, idx) => (
                                    <li key={idx} className="text-sm text-muted-foreground">{concern}</li>
                                  ))}
                                </ul>
                              </div>
                            )}

                            <div className="flex gap-2 pt-2">
                              <Button size="sm" variant="outline" className="flex-1">View Application</Button>
                              <Button size="sm" className="flex-1">Start Match</Button>
                              <Button size="sm" variant="outline">
                                <Mail className="w-4 h-4 mr-2" />
                                Generate Email
                              </Button>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="font-semibold mb-3">📧 Communications Log:</h3>
                  <div className="space-y-2">
                    {dog.matching.communications.map((comm, index) => (
                      <div key={index} className="flex items-center gap-3 text-sm p-2 bg-muted rounded">
                        <Calendar className="w-4 h-4 text-muted-foreground" />
                        <span className="text-muted-foreground">{comm.date}:</span>
                        <span>{comm.action}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Tab 4: History & Notes */}
          <TabsContent value="history" className="mt-6 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>📝 Internal Notes & History</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <h3 className="font-semibold mb-3">Rescue History:</h3>
                  <div className="space-y-3 bg-muted p-4 rounded-lg">
                    <div>
                      <p className="text-sm font-semibold">• Found: {dog.rescueHistory.found.date}</p>
                      <p className="text-sm text-muted-foreground ml-4">
                        Location: {dog.rescueHistory.found.location}
                      </p>
                      <p className="text-sm text-muted-foreground ml-4">
                        Condition: {dog.rescueHistory.found.condition}
                      </p>
                      <p className="text-sm text-muted-foreground ml-4">
                        Rescued by: {dog.rescueHistory.found.rescuedBy}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-semibold">• Intake: {dog.rescueHistory.intake.date}</p>
                      <p className="text-sm text-muted-foreground ml-4">{dog.rescueHistory.intake.notes}</p>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="font-semibold mb-3">Staff Notes (most recent first):</h3>
                  <div className="space-y-3">
                    {dog.staffNotesHistory.map((note, index) => (
                      <Card key={index}>
                        <CardContent className="p-4">
                          <div className="flex items-start justify-between mb-2">
                            <p className="text-sm font-semibold">{note.date} - {note.author}:</p>
                          </div>
                          <p className="text-sm">{note.note}</p>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                  <div className="mt-4">
                    <Textarea
                      placeholder="Add a new note..."
                      value={newNote}
                      onChange={(e) => setNewNote(e.target.value)}
                      className="mb-2"
                    />
                    <Button size="sm">
                      <Plus className="w-4 h-4 mr-2" />
                      Add Note
                    </Button>
                  </div>
                  <Button size="sm" variant="link" className="mt-2">
                    View All Notes (45)
                  </Button>
                </div>

                <div>
                  <h3 className="font-semibold mb-3">🔄 Status Change Log:</h3>
                  <div className="space-y-2">
                    {dog.statusChangeLog.map((log, index) => (
                      <div key={index} className="flex items-center gap-3 text-sm p-2 bg-muted rounded">
                        <Calendar className="w-4 h-4 text-muted-foreground" />
                        <span className="text-muted-foreground">{log.date}:</span>
                        <span>
                          {log.from ? `${log.from} →` : ""} {log.to}
                          {index === 0 && <Badge variant="secondary" className="ml-2">Current</Badge>}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>

      {/* Bottom Action Bar */}
      <div className="fixed bottom-0 left-0 right-0 bg-card border-t border-border shadow-lg z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex gap-3 max-w-2xl mx-auto">
            <Button variant="outline" size="lg" className="flex-1">
              <Mail className="w-4 h-4 mr-2" />
              Email This Profile
            </Button>
            <Button variant="outline" size="lg">
              <Archive className="w-4 h-4 mr-2" />
              Archive Dog
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DogProfilePage;
