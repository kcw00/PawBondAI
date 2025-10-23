// Mock data for conversational search scenarios

export const behavioralMatchAdopters = [
  {
    name: "Sarah Chen",
    location: "Seattle, WA",
    housing: "House with yard",
    score: 94,
    highlights: [
      "Works from home (perfect for separation anxiety!)",
      "Previously rehabilitated anxious rescue dog",
      "Patient, calm lifestyle with proven track record",
    ],
    explanation: {
      semantic: 0.91,
      reason: "Strong semantic match - mentioned 'patient with anxious behaviors' and 'separation anxiety experience'",
      structured: "Employment: Work from home (100% match for separation anxiety needs)",
      experience: "Successfully adopted anxious German Shepherd in 2019, worked with behavioral trainer for 6 months",
    },
  },
  {
    name: "Mike Torres",
    location: "Portland, OR",
    housing: "House with fenced yard",
    score: 89,
    highlights: [
      "Retired teacher - home all day",
      "Specialized in fearful/anxious dogs",
      "Quiet neighborhood, no other pets",
    ],
    explanation: {
      semantic: 0.87,
      reason: "Vector match on 'anxiety', 'patient', 'fearful dog experience'",
      structured: "Employment: Retired = constant presence for anxious dogs",
      experience: "Has fostered 3 anxious dogs, all successful placements",
    },
  },
  {
    name: "Lisa Park",
    location: "Vancouver, BC",
    housing: "Apartment with dog park access",
    score: 86,
    highlights: [
      "Dog trainer specializing in anxiety",
      "Flexible work schedule",
      "Previous anxious dog adopter",
    ],
    explanation: {
      semantic: 0.85,
      reason: "Professional expertise with anxiety cases",
      structured: "Occupation: Dog trainer = expert level",
      experience: "Professional dog trainer for 8 years, focus on rehabilitation",
    },
  },
];

export const multiCriteriaAdopters = [
  {
    name: "Emily Rodriguez",
    location: "Denver, CO",
    housing: "House with large fenced yard",
    score: 96,
    highlights: [
      "Works from home as software engineer",
      "Large fenced yard (0.5 acre)",
      "15+ years senior dog experience",
      "Budget set aside for medical needs",
    ],
    explanation: {
      semantic: 0.92,
      reason: "Perfect match on all criteria - senior dog lover, medical experience",
      structured: "✓ Remote work ✓ House ✓ Yard ✓ Senior experience ✓ Medical budget",
      experience: "Adopted 4 senior dogs over 15 years, including 2 with chronic conditions",
    },
  },
  {
    name: "David Kim",
    location: "Austin, TX",
    housing: "House with yard",
    score: 91,
    highlights: [
      "Retired veterinarian - home all day",
      "Fenced backyard with dog run",
      "Expert in senior dog medical care",
      "Previous hospice foster parent",
    ],
    explanation: {
      semantic: 0.89,
      reason: "Medical expertise ideal for senior dogs with health needs",
      structured: "✓ Retired ✓ House ✓ Yard ✓ Medical expert ✓ Senior experience",
      experience: "Veterinarian for 30 years, fostered 12+ senior/medical needs dogs",
    },
  },
  {
    name: "Jennifer Wu",
    location: "San Diego, CA",
    housing: "House with yard",
    score: 88,
    highlights: [
      "Freelance writer - very flexible schedule",
      "Large yard with shade",
      "5 senior dog adoptions",
      "Strong financial stability",
    ],
    explanation: {
      semantic: 0.86,
      reason: "Strong track record with senior dogs, understands medical costs",
      structured: "✓ Work from home ✓ House ✓ Yard ✓ Senior experience ✓ Financially stable",
      experience: "Adopted 5 senior dogs, all lived comfortably for their remaining years",
    },
  },
];

export const similaritySearchAdopters = [
  {
    name: "Sarah Chen",
    location: "Seattle, WA",
    housing: "House with yard",
    score: 89,
    highlights: [
      "Software engineer, work from home",
      "Previous anxious rescue (German Shepherd)",
      "Patient personality, 6-month training commitment",
    ],
    explanation: {
      semantic: 0.89,
      reason: "Vector similarity to Emily Rodriguez profile - same occupation, WFH, anxious dog experience",
      structured: "Profile match: Tech background, remote work, proven patience with behavioral issues",
      experience: "Adopted Max (anxious rescue) in 2019, successful long-term outcome",
    },
  },
  {
    name: "Mike Torres",
    location: "Portland, OR",
    housing: "House with fenced yard",
    score: 84,
    highlights: [
      "Works remotely as data analyst",
      "Fostered anxious senior Lab mix",
      "Behavioral training background",
    ],
    explanation: {
      semantic: 0.84,
      reason: "Similar work situation and dog experience profile to Emily",
      structured: "Remote work + senior dog experience + training knowledge",
      experience: "Fostered and adopted senior anxious dogs, knows the commitment",
    },
  },
  {
    name: "Rachel Kim",
    location: "Vancouver, BC",
    housing: "Townhouse with yard",
    score: 82,
    highlights: [
      "Freelance designer - flexible schedule",
      "Adopted senior with separation anxiety",
      "Calm, quiet home environment",
    ],
    explanation: {
      semantic: 0.82,
      reason: "Similar lifestyle and dog preference profile",
      structured: "Flexible schedule + anxiety experience + quiet home",
      experience: "Successfully adopted senior anxious dog, excellent follow-up reports",
    },
  },
  {
    name: "James Wilson",
    location: "Seattle, WA",
    housing: "House",
    score: 81,
    highlights: [
      "Software engineer, remote position",
      "Previous anxious senior adoption",
      "Patient, methodical approach",
    ],
    explanation: {
      semantic: 0.81,
      reason: "Very similar profile: tech worker, WFH, anxious senior dog experience",
      structured: "Same city, same industry, same dog preferences as Emily",
      experience: "Adopted Bella (anxious senior) in 2024, thriving adoption",
    },
  },
  {
    name: "Lisa Martinez",
    location: "San Francisco, CA",
    housing: "House with yard",
    score: 79,
    highlights: [
      "Tech startup founder, flexible hours",
      "Multiple senior dog adoptions",
      "Strong support system",
    ],
    explanation: {
      semantic: 0.79,
      reason: "Similar professional background and senior dog focus",
      structured: "Tech industry + flexible schedule + senior dog advocate",
      experience: "Adopted 3 senior dogs over 10 years, all successful outcomes",
    },
  },
];

export const queryInsights = {
  behavioral: {
    parsedQuery: {
      entities: ["separation anxiety", "anxious dog", "patient handler"],
      intent: "find_adopter_by_expertise",
      filters: 'experience_with_anxiety = true',
    },
    semanticSearch: {
      weight: 0.7,
      fields: [
        "application.behavioral_experience",
        "application.previous_challenges",
        "application.patience_indicators"
      ],
      model: "text-embedding-004",
      dimensions: 768,
    },
    structuredSearch: {
      weight: 0.3,
      filters: [
        { key: "employment_status", value: "remote OR retired" },
        { key: "anxious_dog_experience", value: true },
        { key: "behavioral_training", value: true },
      ],
    },
    execution: {
      queryTime: "142ms",
      docsScanned: 203,
      results: 8,
      topScores: [
        { name: "Sarah Chen", score: 0.94 },
        { name: "Mike Torres", score: 0.89 },
        { name: "Lisa Park", score: 0.86 },
      ],
    },
  },
  multiCriteria: {
    parsedQuery: {
      entities: ["work from home", "yard", "senior experience", "medical needs"],
      intent: "find_adopter_multi_requirements",
      filters: 'employment_status = "remote" AND has_yard = true AND senior_experience = true',
    },
    semanticSearch: {
      weight: 0.5,
      fields: [
        "application.motivation_text",
        "application.experience_description",
        "application.medical_preparedness"
      ],
      model: "text-embedding-004",
      dimensions: 768,
    },
    structuredSearch: {
      weight: 0.5,
      filters: [
        { key: "employment_status", value: "remote" },
        { key: "housing_type", value: "house" },
        { key: "has_yard", value: true },
        { key: "senior_experience", value: true },
        { key: "medical_budget", value: true },
      ],
    },
    execution: {
      queryTime: "168ms",
      docsScanned: 203,
      results: 3,
      topScores: [
        { name: "Emily Rodriguez", score: 0.96 },
        { name: "David Kim", score: 0.91 },
        { name: "Jennifer Wu", score: 0.88 },
      ],
    },
  },
  similarity: {
    parsedQuery: {
      entities: ["Emily Rodriguez profile"],
      intent: "find_similar_adopters",
      filters: 'successful_adoption = true',
    },
    semanticSearch: {
      weight: 0.9,
      fields: [
        "adopter.full_profile_embedding",
        "adopter.application_text",
        "adopter.lifestyle_description"
      ],
      model: "text-embedding-004",
      dimensions: 768,
    },
    structuredSearch: {
      weight: 0.1,
      filters: [
        { key: "adoption_outcome", value: "successful" },
        { key: "dog_type", value: "anxious senior" },
      ],
    },
    execution: {
      queryTime: "125ms",
      docsScanned: 203,
      results: 5,
      topScores: [
        { name: "Sarah Chen", score: 0.89 },
        { name: "Mike Torres", score: 0.84 },
        { name: "Rachel Kim", score: 0.82 },
      ],
    },
  },
};
