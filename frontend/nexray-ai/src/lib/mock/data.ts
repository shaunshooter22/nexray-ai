import type { ConditionFinding, ReportRow, SymptomAssessment, XRayAnalysisResult } from "@/types/medical";

export const MOCK_CHEST_FINDINGS: ConditionFinding[] = [
  {
    id: "f1",
    condition: "Pneumonia (right lower lobe)",
    confidence: 87,
    severity: "urgent",
    explanation:
      "Increased opacity consistent with consolidation was detected in the right lower lung field.",
    suggestedTests: ["Sputum culture", "CBC", "CRP"],
    treatment: "Empirical antibiotics pending culture results; monitor oxygen saturation.",
  },
  {
    id: "f2",
    condition: "Mild cardiomegaly",
    confidence: 42,
    severity: "moderate",
    explanation: "Cardiothoracic ratio is slightly above normal range on this projection.",
    suggestedTests: ["Echocardiogram"],
    treatment: "Clinical correlation recommended; not urgent in isolation.",
  },
];

export function mockXRayResult(region: "chest" | "bone" | "spine", imageUrl: string): XRayAnalysisResult {
  return {
    id: "xr-" + Math.random().toString(36).slice(2, 8),
    region,
    detectedRegionConfidence: 96,
    imageUrl,
    findings: region === "chest" ? MOCK_CHEST_FINDINGS : [
      {
        id: "f1",
        condition: region === "bone" ? "Distal radius fracture" : "Mild scoliosis (thoracic)",
        confidence: 81,
        severity: "urgent",
        explanation:
          region === "bone"
            ? "A cortical discontinuity is visible near the distal radius, consistent with a fracture."
            : "A lateral curvature of approximately 12° was measured in the thoracic spine.",
        suggestedTests: region === "bone" ? ["CT for surgical planning"] : ["Orthopedic referral"],
        treatment: region === "bone" ? "Immobilize and refer to orthopedics." : "Monitor; physiotherapy referral.",
      },
    ],
    overallUrgency: region === "chest" ? "urgent" : region === "bone" ? "urgent" : "moderate",
    recommendations: [
      "Correlate findings with clinical presentation",
      "Consider follow-up imaging in 2–4 weeks",
      "Escalate to a radiologist for formal read",
    ],
    analyzedAt: new Date().toISOString(),
  };
}

export function mockSymptomAssessment(symptoms: string): SymptomAssessment {
  const lower = symptoms.toLowerCase();
  if (lower.includes("fever") && (lower.includes("chill") || lower.includes("sweat"))) {
    return {
      likelyCondition: "Malaria",
      confidence: 78,
      recommendedTests: ["Malaria rapid diagnostic test", "Full blood count"],
      suggestedTreatment: "Artemisinin-based combination therapy (ACT) per national guidelines if confirmed.",
      nextSteps: ["Confirm with RDT or blood film", "Monitor temperature and hydration"],
      urgency: "moderate",
    };
  }
  return {
    likelyCondition: "Undifferentiated febrile illness",
    confidence: 54,
    recommendedTests: ["Full blood count", "Malaria RDT", "Widal test"],
    suggestedTreatment: "Supportive care; treat based on confirmed test results.",
    nextSteps: ["Broaden differential with lab tests", "Reassess in 24–48 hours if symptoms persist"],
    urgency: "routine",
  };
}

export const MOCK_REPORTS: ReportRow[] = [
  { id: "r1", patientId: "#2291", patientName: "Kwabena Mensah", type: "Chest X-Ray", date: "24 Jul 2026", status: "Reviewed", urgency: "urgent" },
  { id: "r2", patientId: "#2288", patientName: "Abena Owusu", type: "Bone X-Ray", date: "23 Jul 2026", status: "Pending", urgency: "moderate" },
  { id: "r3", patientId: "#2276", patientName: "Yaw Darko", type: "Spine X-Ray", date: "21 Jul 2026", status: "Critical", urgency: "critical" },
  { id: "r4", patientId: "#2265", patientName: "Efua Asante", type: "Symptom Check", date: "20 Jul 2026", status: "Reviewed", urgency: "routine" },
  { id: "r5", patientId: "#2251", patientName: "Kofi Boateng", type: "Combined", date: "18 Jul 2026", status: "Reviewed", urgency: "moderate" },
  { id: "r6", patientId: "#2240", patientName: "Ama Serwaa", type: "Chest X-Ray", date: "17 Jul 2026", status: "Reviewed", urgency: "routine" },
  { id: "r7", patientId: "#2233", patientName: "Kojo Antwi", type: "Bone X-Ray", date: "15 Jul 2026", status: "Pending", urgency: "urgent" },
  { id: "r8", patientId: "#2219", patientName: "Adjoa Frimpong", type: "Symptom Check", date: "12 Jul 2026", status: "Reviewed", urgency: "routine" },
];
