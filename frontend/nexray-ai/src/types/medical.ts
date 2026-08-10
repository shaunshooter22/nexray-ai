export type Urgency = "routine" | "moderate" | "urgent" | "critical";

export type XRayRegion = "chest" | "bone" | "spine";

export interface ConditionFinding {
  id: string;
  condition: string;
  confidence: number; // 0-100
  severity: Urgency;
  explanation: string;
  suggestedTests: string[];
  treatment: string;
}

export interface XRayAnalysisResult {
  id: string;
  region: XRayRegion;
  detectedRegionConfidence: number;
  imageUrl: string;
  findings: ConditionFinding[];
  overallUrgency: Urgency;
  recommendations: string[];
  analyzedAt: string;
}

export interface SymptomAssessment {
  likelyCondition: string;
  confidence: number;
  recommendedTests: string[];
  suggestedTreatment: string;
  nextSteps: string[];
  urgency: Urgency;
}

export interface PatientInfo {
  name: string;
  patientId: string;
  age: number;
  gender: "Male" | "Female" | "Other";
  duration?: string;
  medicalHistory?: string;
}

export interface ReportRow {
  id: string;
  patientId: string;
  patientName: string;
  type: "Chest X-Ray" | "Bone X-Ray" | "Spine X-Ray" | "Symptom Check" | "Combined";
  date: string;
  status: "Reviewed" | "Pending" | "Critical";
  urgency: Urgency;
}
