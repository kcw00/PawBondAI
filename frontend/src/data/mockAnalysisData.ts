export const mockAnalysisData = {
  applicantName: "Sarah Chen",
  strengths: [
    "Works from home (reliability score: 0.94)",
    "Previous anxious rescue experience (expertise: 0.91)",
    "Patience & long-term commitment (sentiment: 0.88)",
    "Financial preparedness mentioned",
    "Behavioral training background",
    "Suitable housing: house + yard"
  ],
  experienceLevel: "ADVANCED",
  bestSuitedFor: ["Anxious/fearful", "Senior", "Medical needs"],
  similarAdopters: [
    {
      name: "Emily Rodriguez",
      similarity: 89,
      dogName: "Rocky (fearful Lab mix)",
      dogAge: 9,
      adoptionDate: "March 2024",
      outcome: "successful" as const,
      traits: [
        "Work from home: ✓",
        "Previous anxious dog experience: ✓",
        "Patient, calm approach: ✓"
      ],
      followUp: [
        "Week 2: Still hiding, but eating regularly",
        "Week 6: First tail wag! Progress is slow but steady",
        "Month 3: Rocky is thriving! Sleeps on the couch now"
      ],
      successFactors: [
        "WFH schedule allowed consistent routine",
        "Realistic expectations (didn't rush progress)",
        "Financial stability for behavioral training",
        "Quiet home environment"
      ]
    },
    {
      name: "James Wilson",
      similarity: 86,
      dogName: "Bella (anxious senior)",
      dogAge: 11,
      adoptionDate: "January 2024",
      outcome: "successful" as const,
      traits: [
        "Software engineer working remotely",
        "Previous rescue with separation anxiety",
        "Patient, willing to invest time"
      ],
      followUp: [
        "Week 1: Bella very scared, won't leave corner",
        "Month 1: Starting to trust, takes treats from hand",
        "Month 4: Complete transformation, loves cuddles"
      ],
      successFactors: [
        "Remote work provided constant presence",
        "Previous experience with anxious dogs",
        "Consulted with behavioral specialist",
        "No young children in home"
      ]
    },
    {
      name: "Maria Santos",
      similarity: 84,
      dogName: "Duke (fearful senior)",
      dogAge: 8,
      adoptionDate: "November 2023",
      outcome: "successful" as const,
      traits: [
        "Retired, home all day",
        "Experience with senior dogs",
        "Calm, patient personality"
      ],
      followUp: [
        "Week 3: Duke slowly warming up",
        "Month 2: First walk outside!",
        "Month 5: Duke is my shadow, so loving"
      ],
      successFactors: [
        "Retirement allowed unlimited time",
        "No other pets to stress Duke",
        "Experience managing medical needs",
        "Strong support system"
      ]
    }
  ],
  successRate: 87,
  successFactors: {
    "Works from home": 73,
    "Previous anxious dog experience": 81,
    "Average adjustment time: 6-8 weeks": 100,
    "Zero returns with this profile": 100
  },
  recommendedDogs: [
    {
      id: "luna",
      name: "Luna",
      breed: "Korean Jindo Mix",
      age: 8,
      matchScore: 94,
      reasons: [
        "Anxious/fearful personality (matches experience)",
        "Senior dog (matches preference)",
        "Needs calm, patient home (perfect fit)",
        "Medical needs manageable (heartworm treatment)"
      ],
      similarPairing: "Emily + Rocky (same profile, 89% similar)"
    },
    {
      id: "buddy",
      name: "Buddy",
      breed: "Lab Mix",
      age: 9,
      matchScore: 91,
      reasons: [
        "Gentle senior with anxiety history",
        "Loves quiet home environments",
        "Responds well to patient handling",
        "No special medical needs"
      ],
      similarPairing: "James + Bella (86% similar profile)"
    },
    {
      id: "max",
      name: "Max",
      breed: "Beagle Mix",
      age: 10,
      matchScore: 88,
      reasons: [
        "Senior with fearful tendencies",
        "Needs experienced handler",
        "Thrives with routine and consistency",
        "Low energy, perfect for calm home"
      ],
      similarPairing: "Maria + Duke (84% similar profile)"
    }
  ],
  elasticsearchQuery: {
    parsedQuery: {
      entities: ["work from home", "anxiety experience"],
      intent: "find_adopter",
      filters: 'experience_level >= "some"'
    },
    semanticSearch: {
      weight: 0.7,
      fields: [
        "application.motivation_text",
        "application.experience_description",
        "application.lifestyle_notes"
      ],
      model: "text-embedding-004",
      dimensions: 768
    },
    structuredSearch: {
      weight: 0.3,
      filters: [
        { key: "employment_status", value: "remote" },
        { key: "previous_dog", value: true },
        { key: "anxiety_experience", value: true }
      ]
    },
    execution: {
      queryTime: "156ms",
      docsScanned: 203,
      results: 47,
      topScores: [
        { name: "Emily Rodriguez", score: 0.89 },
        { name: "James Wilson", score: 0.86 },
        { name: "Maria Santos", score: 0.84 }
      ]
    }
  }
};
