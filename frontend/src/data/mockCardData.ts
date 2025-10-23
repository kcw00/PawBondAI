// Mock data for testing all card components

export const mockApplicationMatches = [
  {
    applicantName: "Sarah Chen",
    applicantPhoto: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&h=400&fit=crop",
    matchScore: 92,
    location: "Seattle, WA",
    distance: "2.3 miles",
    housing: "House with large fenced yard",
    compatibilityFactors: [
      { icon: "home", text: "Works from home - perfect for anxious dogs" },
      { icon: "heart", text: "Previous experience with senior rescues" },
      { icon: "check", text: "Patient, calm household environment" },
      { icon: "users", text: "Active in local rescue community" }
    ],
    explanation: {
      semanticScore: 0.89,
      semanticReason: "Applicant specifically mentioned experience with anxious behaviors and separation anxiety in their application essay.",
      structuredMatches: [
        "Housing: House with yard ✓",
        "Work schedule: Remote/Flexible ✓",
        "Experience level: Advanced ✓",
        "Pet history: Successful adoptions ✓"
      ],
      pastSuccessIndicators: [
        "Successfully fostered 3 anxious dogs in 2022-2023",
        "Completed positive reinforcement training course",
        "References from veterinarian and previous rescue"
      ]
    }
  },
  {
    applicantName: "Michael Rodriguez",
    applicantPhoto: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop",
    matchScore: 78,
    location: "Portland, OR",
    distance: "15.7 miles",
    housing: "Apartment with nearby dog park",
    compatibilityFactors: [
      { icon: "activity", text: "Active lifestyle - runs 5 miles daily" },
      { icon: "award", text: "Experience with high-energy breeds" },
      { icon: "clock", text: "Flexible work schedule" },
      { icon: "users", text: "Strong support network" }
    ],
    explanation: {
      semanticScore: 0.76,
      semanticReason: "Good match for energy requirements and lifestyle compatibility.",
      structuredMatches: [
        "Housing: Apartment ✓",
        "Activity level: High ✓",
        "Experience level: Intermediate ✓"
      ],
      pastSuccessIndicators: [
        "Previously owned Australian Shepherd for 8 years",
        "Regular volunteer at local shelter"
      ]
    }
  }
];

export const mockDogProfiles = [
  {
    name: "Luna",
    age: "3 years old",
    breed: "Mixed Breed (Lab/Shepherd)",
    photos: [
      "https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?w=800&h=600&fit=crop",
      "https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=800&h=600&fit=crop",
      "https://images.unsplash.com/photo-1477884213360-7e9d7dcc1e48?w=800&h=600&fit=crop"
    ],
    personalityTags: ["Gentle", "Anxious", "Food-motivated", "Loves walks", "Quiet"],
    status: "Available" as const,
    specialNeeds: "Needs experienced owner comfortable with separation anxiety. No small children.",
    energyLevel: "Moderate" as const,
    size: "Large" as const,
    goodWithKids: false,
    goodWithPets: true,
    hasKoreanProfile: true
  },
  {
    name: "Max",
    age: "7 years old",
    breed: "Golden Retriever",
    photos: [
      "https://images.unsplash.com/photo-1633722715463-d30f4f325e24?w=800&h=600&fit=crop",
      "https://images.unsplash.com/photo-1612536916398-de596b1c0a12?w=800&h=600&fit=crop"
    ],
    personalityTags: ["Calm", "Affectionate", "Senior", "Gentle", "Patient"],
    status: "Medical Hold" as const,
    specialNeeds: "Requires arthritis medication twice daily. Prefers quiet homes.",
    energyLevel: "Low" as const,
    size: "Large" as const,
    goodWithKids: true,
    goodWithPets: true,
    hasKoreanProfile: false
  }
];

export const mockSearchExplanations = [
  {
    queryBreakdown: "Find adopters for anxious senior dogs",
    semanticComponent: {
      keyPhrases: ["anxious", "senior dogs", "experienced handler", "patient environment"],
      embeddingSimilarity: 0.85
    },
    structuredFilters: [
      { label: "Housing Type", value: "House preferred" },
      { label: "Experience Level", value: "Intermediate to Advanced" },
      { label: "Work Schedule", value: "Flexible or Remote" },
      { label: "Location Radius", value: "25 miles from rescue center" }
    ],
    resultsCount: 47,
    totalDocuments: 1250,
    queryTimeMs: 127
  },
  {
    queryBreakdown: "Applications for high-energy dogs with yard access",
    semanticComponent: {
      keyPhrases: ["high-energy", "active lifestyle", "yard", "outdoor space"],
      embeddingSimilarity: 0.91
    },
    structuredFilters: [
      { label: "Housing Type", value: "House with yard (required)" },
      { label: "Activity Level", value: "High" },
      { label: "Location Radius", value: "50 miles from rescue center" }
    ],
    resultsCount: 23,
    totalDocuments: 1250,
    queryTimeMs: 89
  }
];

export const mockTranslations = [
  {
    originalLanguage: "Korean",
    originalLanguageCode: "ko",
    originalText: "루나는 3살 암컷 믹스견입니다. 분리불안이 있어 혼자 있는 것을 어려워합니다. 천천히 적응하는 편이며, 간식을 좋아합니다. 다른 개들과는 잘 지내지만, 어린 아이들은 무서워합니다.",
    translatedText: "Luna is a 3-year-old female mixed breed dog. She has separation anxiety and struggles with being alone. She tends to adapt slowly and loves treats. She gets along well with other dogs but is afraid of young children.",
    medicalTerms: [
      { term: "separation anxiety", position: 42 },
      { term: "mixed breed", position: 20 },
      { term: "adapt slowly", position: 105 }
    ],
    confidenceScore: 0.94
  },
  {
    originalLanguage: "Korean",
    originalLanguageCode: "ko",
    originalText: "건강검진 결과: 심장사상충 음성, 모든 예방접종 완료. 경미한 관절염 있음 - 글루코사민 보충제 권장. 치아 상태 양호.",
    translatedText: "Health examination results: Heartworm negative, all vaccinations completed. Mild arthritis present - glucosamine supplement recommended. Dental condition good.",
    medicalTerms: [
      { term: "Heartworm negative", position: 28 },
      { term: "vaccinations", position: 50 },
      { term: "arthritis", position: 75 },
      { term: "glucosamine supplement", position: 95 },
      { term: "Dental condition", position: 132 }
    ],
    confidenceScore: 0.97
  }
];

export const mockCaseStudies = [
  {
    location: "Portland, OR",
    date: "March 2024",
    dogDescription: "4-year-old mixed breed with severe separation anxiety",
    situation: "Dog was returned twice due to destructive behavior when left alone. Previous adopters worked full-time office jobs.",
    solutionApplied: "Matched with remote worker who could provide gradual alone-time training. Recommended certified trainer specializing in anxiety.",
    outcome: "success" as const,
    outcomeDetails: "After 6 weeks of consistent training, dog can now be alone for 4-5 hours comfortably. Adopter reports significant improvement.",
    similarityScore: 0.91,
    caseId: "CASE-2024-0342"
  },
  {
    location: "Seattle, WA",
    date: "January 2024",
    dogDescription: "Senior golden retriever with arthritis",
    situation: "Dog needed adopter who could manage medical care and provide low-impact exercise.",
    solutionApplied: "Matched with retired couple experienced with senior dogs. Provided detailed care plan and medication schedule.",
    outcome: "success" as const,
    outcomeDetails: "Dog thriving in new home. Adopters report excellent quality of life with proper pain management.",
    similarityScore: 0.87,
    caseId: "CASE-2024-0128"
  },
  {
    location: "Tacoma, WA",
    date: "February 2024",
    dogDescription: "High-energy husky mix requiring extensive exercise",
    situation: "Dog was surrendered due to excessive energy and destructive behavior in apartment setting.",
    solutionApplied: "Matched with active family in suburban home. However, family underestimated exercise requirements.",
    outcome: "failed" as const,
    outcomeDetails: "Dog returned after 3 weeks. Family couldn't maintain 2+ hours of daily exercise. Re-matched with marathon runner - successful second placement.",
    similarityScore: 0.73,
    caseId: "CASE-2024-0215"
  }
];

export const mockSuccessCases = [
  {
    dogName: "Max",
    dogPhoto: "https://images.unsplash.com/photo-1633722715463-d30f4f325e24?w=400&h=400&fit=crop",
    breed: "German Shepherd Mix",
    location: "Seattle Rescue Center",
    adoptionDate: "Jan 2024",
    similarConditions: ["Heartworm positive", "Malnutrition", "Anxiety"],
    similarityScore: 0.94,
    journeySteps: {
      initialCondition: "Critical - same as Luna (heartworm positive, severe malnutrition)",
      treatmentDuration: "7 months of intensive treatment",
      adopterProfile: "Experienced foster family with medical background",
      currentStatus: "Thriving! Verified follow-up shows full recovery"
    },
    successFactors: [
      "Adopter worked from home - could monitor medication schedule closely",
      "Previous experience with 3 medical-needs dogs over 10 years",
      "Financial stability to cover $80-120/month in ongoing care",
      "Patient, calm household with no other pets during recovery",
      "Strong relationship with local vet clinic",
      "Dedicated quiet space for recovery and rest"
    ],
    caseId: "SUCCESS-2024-0089"
  },
  {
    dogName: "Bella",
    dogPhoto: "https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=400&h=400&fit=crop",
    breed: "Labrador Mix",
    location: "Portland Rescue",
    adoptionDate: "Mar 2024",
    similarConditions: ["Heartworm positive", "Underweight"],
    similarityScore: 0.89,
    journeySteps: {
      initialCondition: "Moderate heartworm infestation, 15 lbs underweight",
      treatmentDuration: "6 months - adopted during treatment period",
      adopterProfile: "Retired couple, wife is former veterinary nurse",
      currentStatus: "Fully recovered, happy and healthy life"
    },
    successFactors: [
      "Adopters were retired - had unlimited time for care and vet visits",
      "Wife's medical background meant she understood all terminology",
      "Committed to seeing treatment through from day one",
      "Strong support from rescue team with weekly check-ins",
      "Adopted during treatment (fostered first, then adopted)",
      "Created detailed care journal to track progress"
    ],
    caseId: "SUCCESS-2024-0102"
  },
  {
    dogName: "Rocky",
    dogPhoto: "https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?w=400&h=400&fit=crop",
    breed: "Mixed Breed",
    location: "Vancouver Rescue",
    adoptionDate: "Dec 2023",
    similarConditions: ["Heartworm positive", "Behavioral issues"],
    similarityScore: 0.86,
    journeySteps: {
      initialCondition: "Initially considered 'unadoptable' - heartworm + severe anxiety",
      treatmentDuration: "8-month treatment + behavioral rehabilitation program",
      adopterProfile: "Experienced dog trainer who specifically wanted project dog",
      currentStatus: "Therapy dog in training! Incredible transformation"
    },
    successFactors: [
      "Adopter specifically wanted a 'project dog' to work with",
      "Professional experience with anxious rescues (10+ years)",
      "Worked with veterinary behaviorist throughout process",
      "Incredible patience and dedication to training",
      "Used positive reinforcement methods exclusively",
      "Now helps rehabilitate other rescue dogs"
    ],
    caseId: "SUCCESS-2023-0456"
  }
];

export const mockPhotoAnalysis = {
  imageUrl: "https://images.unsplash.com/photo-1633722715463-d30f4f325e24?w=800&h=600&fit=crop",
  breed: "Likely Golden Retriever mix",
  breedConfidence: 0.87,
  estimatedAge: "6-8 years",
  ageIndicators: [
    "Gray muzzle and around eyes",
    "Slight cloudiness in eye clarity typical of senior dogs",
    "Mature facial structure"
  ],
  bodyCondition: "Healthy weight, good coat condition",
  behavioralCues: [
    "Relaxed posture indicates comfortable temperament",
    "Friendly, open expression",
    "Direct eye contact suggests confidence",
    "Ears in neutral position - calm state"
  ],
  healthConcerns: [],
  overallAssessment: "good" as const
};

export const mockMedicalDocument = {
  documentUrl: "https://images.unsplash.com/photo-1586281380349-632531db7ed4?w=400&h=600&fit=crop",
  dogName: "Luna",
  processingSteps: {
    ocrComplete: true,
    translationComplete: true,
    conditionsIdentified: true,
    casesSearched: true
  },
  primaryConditions: [
    {
      name: "Heartworm (Dirofilaria immitis) - Positive",
      severity: "critical" as const,
      status: "active" as const
    },
    {
      name: "Severe Malnutrition (Body Condition Score 2/9)",
      severity: "critical" as const,
      status: "active" as const
    },
    {
      name: "Mild Anemia (likely secondary to heartworm)",
      severity: "moderate" as const,
      status: "monitoring" as const
    }
  ],
  treatments: [
    {
      medication: "Ivermectin + Doxycycline",
      dosage: "Ivermectin 6mcg/kg, Doxycycline 10mg/kg",
      frequency: "Daily for 30 days, then monthly prevention",
      startDate: "Sept 15, 2024",
      duration: "6-8 months treatment protocol"
    },
    {
      medication: "High-calorie recovery diet",
      dosage: "3 cups daily (gradually increasing)",
      frequency: "Split into 3 meals per day",
      startDate: "Sept 15, 2024",
      duration: "Until healthy weight achieved (est. 3-4 months)"
    }
  ],
  followUpSchedule: "Monthly blood tests required. Next heartworm antigen test in 6 months. Weight checks biweekly.",
  prognosis: "Good with continued treatment and proper nutrition. Expected full recovery in 6-8 months with appropriate care.",
  prognosisConfidence: 85,
  adoptionConsiderations: [
    "Needs experienced adopter comfortable with medical management",
    "Ongoing medication costs: ~$80/month during treatment",
    "Regular vet visits required (monthly for first 6 months)",
    "Must be able to monitor for exercise intolerance during recovery",
    "Financial stability important for unexpected complications",
    "Patient household - dog needs low-stress environment"
  ],
  estimatedMonthlyCost: 80
};
