// ============================================================
// NexRay AI - API Service
// All backend calls go through this file.
// Base URL is set via environment variable.
// ============================================================

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// ── Get the stored JWT token ──
export function getToken(): string | null {
  return localStorage.getItem("nexray_token");
}

// ── Auth headers for protected routes ──
function authHeaders(): HeadersInit {
  return {
    "Authorization": `Bearer ${getToken()}`,
    "Content-Type": "application/json",
  };
}

// ══════════════════════════════════════════════
// AUTH
// ══════════════════════════════════════════════

export async function login(email: string, password: string) {
  const res = await fetch(`${BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) throw new Error("Incorrect email or password");
  const data = await res.json();
  localStorage.setItem("nexray_token", data.access_token);
  localStorage.setItem("nexray_doctor", JSON.stringify({
    id: data.doctor_id,
    name: data.full_name,
    email: data.email,
  }));
  return data;
}

export function logout() {
  localStorage.removeItem("nexray_token");
  localStorage.removeItem("nexray_doctor");
  localStorage.removeItem("nexray_analysis");
}

export function getDoctor() {
  const d = localStorage.getItem("nexray_doctor");
  return d ? JSON.parse(d) : null;
}

export function isLoggedIn(): boolean {
  return !!getToken();
}

// ══════════════════════════════════════════════
// COMBINED ANALYSIS
// ══════════════════════════════════════════════

export async function analyze(file?: File, symptoms?: string, patientName?: string) {
  const formData = new FormData();
  if (file) formData.append("file", file);
  if (symptoms) formData.append("symptoms", symptoms);
  if (patientName) formData.append("patient_name", patientName);

  const res = await fetch(`${BASE_URL}/analyze/`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${getToken()}`,
    },
    body: formData,
  });
  if (!res.ok) throw new Error("Analysis failed");
  return res.json();
}

// ══════════════════════════════════════════════
// REFINE DIAGNOSIS
// ══════════════════════════════════════════════

export async function refineDiagnosis(
  sessionId: number,
  testResults: string,
  analysisType: "xray" | "symptoms"
) {
  const res = await fetch(`${BASE_URL}/refine/diagnosis`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({
      session_id: sessionId,
      test_results: testResults,
      analysis_type: analysisType,
    }),
  });
  if (!res.ok) throw new Error("Refinement failed");
  return res.json();
}

// ══════════════════════════════════════════════
// REPORTS
// ══════════════════════════════════════════════

export async function generateReport(sessionId: number) {
  const res = await fetch(`${BASE_URL}/reports/generate`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ session_id: sessionId }),
  });
  if (!res.ok) throw new Error("Report generation failed");
  return res.json();
}

// Opens PDF directly — works on iPhone and Android
export function openReport(reportId: number) {
  const url = `${BASE_URL}/reports/download/${reportId}?token=${getToken()}`;
  window.open(url, "_blank");
}

export async function downloadReport(reportId: number): Promise<Blob> {
  const res = await fetch(`${BASE_URL}/reports/download/${reportId}`, {
    headers: {
      "Authorization": `Bearer ${getToken()}`,
    },
  });
  if (!res.ok) throw new Error("Download failed");
  return res.blob();
}

export async function listReports() {
  const res = await fetch(`${BASE_URL}/reports/list`, {
    headers: {
      "Authorization": `Bearer ${getToken()}`,
    },
  });
  if (!res.ok) throw new Error("Failed to fetch reports");
  return res.json();
}

export async function getStats() {
  const res = await fetch(`${BASE_URL}/reports/stats`, {
    headers: {
      "Authorization": `Bearer ${getToken()}`,
    },
  });
  if (!res.ok) throw new Error("Failed to fetch stats");
  return res.json();
}

export function triggerDownload(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.target = "_blank";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

// ══════════════════════════════════════════════
// SESSION STATE PERSISTENCE
// ══════════════════════════════════════════════

export function saveAnalysisState(state: {
  sessionId: number;
  result: any;
  type: "xray" | "symptoms" | "combined";
  imageBase64?: string;
  analyzing?: boolean;
  symptoms?: string;
  patientName?: string;
}) {
  localStorage.setItem("nexray_analysis", JSON.stringify(state));
}

export function loadAnalysisState() {
  const s = localStorage.getItem("nexray_analysis");
  return s ? JSON.parse(s) : null;
}

export function clearAnalysisState() {
  localStorage.removeItem("nexray_analysis");
}