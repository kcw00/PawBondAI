export const mockBehavioralAnalysis = {
  dogName: "Luna",
  week: 3,
  triggers: [
    { text: "Doorbell (startle response)", severity: "high" as const },
    { text: "Being watched during eating", severity: "high" as const },
    { text: "Sudden movements", severity: "medium" as const }
  ],
  improvements: [
    "First tail wag (major milestone!)",
    "Sleeping in bed vs. under table",
    "Accepts morning petting",
    "Shows trust with primary caregiver"
  ],
  similarCases: [
    {
      dogName: "Rocky",
      breed: "Lab Mix",
      adoptionDate: "March 2024",
      similarity: 84,
      weekThreeReport: "...hiding at loud noises...won't eat if watched...first tail wag this week...",
      timeline: [
        { week: 3, milestone: "First signs of trust (same as Luna)" },
        { week: 6, milestone: "Comfortable with foster family" },
        { week: 8, milestone: "Ready for adoption" }
      ],
      outcome: "Successfully adopted",
      outcomeSuccess: true
    },
    {
      dogName: "Bella",
      breed: "Shepherd Mix",
      adoptionDate: "January 2024",
      similarity: 82,
      weekThreeReport: "...still nervous around strangers...tail wag breakthrough today...sleeping better...",
      timeline: [
        { week: 3, milestone: "First tail wag observed" },
        { week: 5, milestone: "Accepts treats from strangers" },
        { week: 7, milestone: "Adoption ready" }
      ],
      outcome: "Successfully adopted",
      outcomeSuccess: true
    },
    {
      dogName: "Max",
      breed: "Beagle Mix",
      adoptionDate: "November 2023",
      similarity: 79,
      weekThreeReport: "...anxiety around food time...progress with trust building...small victories daily...",
      timeline: [
        { week: 3, milestone: "Trust building progress" },
        { week: 6, milestone: "Comfortable in new environments" },
        { week: 8, milestone: "Ready for forever home" }
      ],
      outcome: "Successfully adopted",
      outcomeSuccess: true
    }
  ],
  predictions: {
    expectedTimeline: [
      { weeks: "Weeks 4-6", milestone: "Continued trust building" },
      { weeks: "Weeks 6-8", milestone: "Ready for meet-and-greets" },
      { weeks: "Week 8-10", milestone: "Likely adoption-ready" }
    ],
    successRate: 89,
    totalSimilarCases: 8
  },
  recommendedAdopter: [
    "Patient, calm personality",
    "Quiet home environment",
    "Experience with fearful dogs",
    "Works from home preferred"
  ]
};

export const behavioralSearchInsights = {
  parsedQuery: {
    entities: ["anxiety triggers", "behavioral progress", "timeline"],
    intent: "analyze_behavior_pattern",
    filters: "week = 3, dog_type = anxious_rescue"
  },
  semanticSearch: {
    weight: "0.8",
    fields: [
      "foster_report.behavioral_notes",
      "foster_report.triggers_description",
      "foster_report.progress_notes"
    ],
    model: "text-embedding-004",
    dimensions: 768
  },
  structuredSearch: {
    weight: "0.2",
    filters: [
      { key: "week_number", value: 3 },
      { key: "anxiety_markers", value: true },
      { key: "positive_progress", value: true }
    ]
  },
  execution: {
    queryTime: "142ms",
    docsScanned: "156 foster reports",
    results: "8 similar cases",
    topScores: [
      { name: "Rocky (Lab Mix)", score: "0.84" },
      { name: "Bella (Shepherd)", score: "0.82" },
      { name: "Max (Beagle)", score: "0.79" }
    ]
  }
};
