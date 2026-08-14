// ============================================================
// NexRay AI - Combined Case Page
// ============================================================

import { useState, useEffect, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Alert } from "@/components/ui/alert";
import { FileUploadCard } from "@/components/medical/FileUploadCard";
import { UrgencyBadge } from "@/components/medical/UrgencyBadge";
import {
  analyze, generateReport, handleReport, refineDiagnosis,
  saveAnalysisState, loadAnalysisState, clearAnalysisState
} from "@/lib/api";
import toast from "react-hot-toast";
import { ListChecks, Download, FileText, Stethoscope, User, FlaskConical, CheckCircle, XCircle } from "lucide-react";

type Stage = "idle" | "analyzing" | "done";

function mapUrgency(urgency: string): "routine" | "moderate" | "urgent" | "critical" {
  const map: Record<string, "routine" | "moderate" | "urgent" | "critical"> = {
    "Routine": "routine",
    "Urgent": "urgent",
    "Emergency": "critical",
  };
  return map[urgency] ?? "routine";
}

function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

export default function NewCombinedCase() {
  const saved = loadAnalysisState();

  const [previewUrl, setPreviewUrl] = useState<string | null>(
    saved?.type === "combined" ? saved?.imageBase64 ?? null : null
  );
  const [symptoms, setSymptoms] = useState("");
  const [patientName, setPatientName] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [stage, setStage] = useState<Stage>(
    saved?.type === "combined" && saved?.result ? "done" :
    saved?.type === "combined" && saved?.analyzing ? "analyzing" : "idle"
  );
  const [result, setResult] = useState<any>(
    saved?.type === "combined" && saved?.result ? saved.result : null
  );
  const [sessionId, setSessionId] = useState<number | null>(
    saved?.type === "combined" && saved?.sessionId ? saved.sessionId : null
  );
  const [savedSymptoms, setSavedSymptoms] = useState<string>(
    saved?.type === "combined" ? saved?.symptoms ?? "" : ""
  );
  const [savedPatientName, setSavedPatientName] = useState<string>(
    saved?.type === "combined" ? saved?.patientName ?? "" : ""
  );
  const [reportId, setReportId] = useState<number | null>(null);
  const [reportLoading, setReportLoading] = useState(false);
  const [testResults, setTestResults] = useState("");
  const [refineLoading, setRefineLoading] = useState(false);
  const [refinedDiagnosis, setRefinedDiagnosis] = useState<any>(null);
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (stage === "analyzing") {
      pollingRef.current = setInterval(() => {
        const latest = loadAnalysisState();
        if (latest?.type === "combined" && latest?.result && !latest?.analyzing) {
          setResult(latest.result);
          setSessionId(latest.sessionId);
          setPreviewUrl(latest.imageBase64 ?? null);
          setSavedSymptoms(latest.symptoms ?? "");
          setSavedPatientName(latest.patientName ?? "");
          setStage("done");
          toast.success("Analysis complete");
          if (pollingRef.current) clearInterval(pollingRef.current);
        }
      }, 1000);
    }
    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current);
    };
  }, [stage]);

  function handleNewCase() {
    clearAnalysisState();
    setPreviewUrl(null);
    setFile(null);
    setSymptoms("");
    setPatientName("");
    setResult(null);
    setSessionId(null);
    setSavedSymptoms("");
    setSavedPatientName("");
    setReportId(null);
    setTestResults("");
    setRefinedDiagnosis(null);
    setStage("idle");
  }

  function handleFile(f: File) {
    setFile(f);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!patientName.trim()) {
      toast.error("Please enter the patient's name");
      return;
    }
    if (!file && !symptoms.trim()) {
      toast.error("Please upload an X-ray or enter symptoms");
      return;
    }

    setStage("analyzing");
    setSavedPatientName(patientName);

    let base64 = "";
    if (file) {
      base64 = await fileToBase64(file);
      setPreviewUrl(base64);
    }

    saveAnalysisState({
      sessionId: 0,
      result: null,
      type: "combined",
      imageBase64: base64 || undefined,
      symptoms: symptoms || undefined,
      patientName: patientName || undefined,
      analyzing: true,
    } as any);

    try {
      const data = await analyze(file || undefined, symptoms || undefined, patientName || undefined);
      saveAnalysisState({
        sessionId: data.session_id,
        result: data.analysis,
        type: "combined",
        imageBase64: base64 || undefined,
        symptoms: symptoms || undefined,
        patientName: patientName || undefined,
        analyzing: false,
      } as any);
      setResult(data.analysis);
      setSessionId(data.session_id);
      setSavedSymptoms(symptoms);
      setStage("done");
      toast.success("Analysis complete");
    } catch (err) {
      toast.error("Analysis failed. Please try again.");
      setStage("idle");
      clearAnalysisState();
    }
  }

  async function handleRefine() {
    if (!testResults.trim()) {
      toast.error("Please enter the test results first");
      return;
    }
    if (!sessionId) return;
    setRefineLoading(true);
    try {
      // Use symptoms if available, otherwise xray
      const analysisType = savedSymptoms ? "symptoms" : "xray";
      const data = await refineDiagnosis(sessionId, testResults, analysisType);
      setRefinedDiagnosis(data.refined_diagnosis);
      setReportId(null);
      toast.success("Diagnosis refined successfully");
    } catch (err) {
      toast.error("Failed to refine diagnosis");
    } finally {
      setRefineLoading(false);
    }
  }

  async function handleDownload() {
    if (!sessionId) return;
    setReportLoading(true);
    try {
      let id = reportId;
      if (!id) {
        const reportData = await generateReport(sessionId);
        id = reportData.report_id;
        setReportId(id);
      }
      await handleReport(id!, savedPatientName);
    } catch (err) {
      toast.error("Failed to get report");
    } finally {
      setReportLoading(false);
    }
  }

  const conditions = result?.possible_conditions || result?.findings || [];

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-page-title text-text-primary">Combined Case</h1>
          <p className="text-body text-text-secondary mt-1">
            Upload an X-ray, enter symptoms, or both together for a combined assessment.
          </p>
        </div>
        {stage === "done" && (
          <Button variant="outline" onClick={handleNewCase}>
            New Case
          </Button>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
        {stage === "idle" && (
          <Card>
            <CardHeader><CardTitle>Case Details</CardTitle></CardHeader>
            <CardContent>
              <form className="flex flex-col gap-5" onSubmit={handleSubmit}>
                <div className="flex flex-col gap-2">
                  <Label htmlFor="patient_name" className="flex items-center gap-2">
                    <User size={14} />
                    Patient Name <span className="text-red-500 ml-1">*</span>
                  </Label>
                  <Input
                    id="patient_name"
                    placeholder="e.g. Kwame Mensah"
                    value={patientName}
                    onChange={(e) => setPatientName(e.target.value)}
                  />
                </div>

                <div className="flex flex-col gap-2">
                  <Label>X-Ray Image (optional)</Label>
                  <FileUploadCard onFileAccepted={handleFile} previewUrl={null} />
                  {file && (
                    <p className="text-tiny text-text-secondary">✓ {file.name} selected</p>
                  )}
                </div>

                <div className="flex flex-col gap-2">
                  <Label htmlFor="symptoms">Symptoms (optional)</Label>
                  <Textarea
                    id="symptoms"
                    placeholder="Describe the patient's symptoms in plain English..."
                    rows={4}
                    value={symptoms}
                    onChange={(e) => setSymptoms(e.target.value)}
                  />
                </div>

                <Button type="submit" className="w-full">
                  <Stethoscope size={16} className="mr-2" />
                  Analyse Case
                </Button>
              </form>
            </CardContent>
          </Card>
        )}

        {stage === "analyzing" && (
          <Card>
            <CardContent className="flex flex-col items-center gap-4 py-12 text-center">
              <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
              <p className="text-card-title text-text-primary">NexRay AI is analysing the case...</p>
              <p className="text-body-sm text-text-secondary">This usually takes a few seconds.</p>
            </CardContent>
          </Card>
        )}

        {stage === "done" && previewUrl && (
          <div className="flex flex-col gap-4">
            <img
              src={previewUrl}
              alt="Uploaded X-ray"
              className="w-full rounded-lg border border-border object-contain max-h-96 bg-black"
            />
            {(savedPatientName || savedSymptoms) && (
              <Alert>
                <Stethoscope size={16} />
                <div className="mt-1 flex flex-col gap-1">
                  {savedPatientName && (
                    <p className="text-body-sm font-medium text-text-primary flex items-center gap-1">
                      <User size={13} /> {savedPatientName}
                    </p>
                  )}
                  {savedSymptoms && (
                    <p className="text-body-sm text-text-secondary italic">"{savedSymptoms}"</p>
                  )}
                </div>
              </Alert>
            )}
          </div>
        )}

        {stage === "done" && !previewUrl && (savedPatientName || savedSymptoms) && (
          <Alert>
            <Stethoscope size={16} />
            <div className="mt-1 flex flex-col gap-1">
              {savedPatientName && (
                <p className="text-body-sm font-medium text-text-primary flex items-center gap-1">
                  <User size={13} /> {savedPatientName}
                </p>
              )}
              {savedSymptoms && (
                <p className="text-body-sm text-text-secondary italic">"{savedSymptoms}"</p>
              )}
            </div>
          </Alert>
        )}

        {stage === "done" && result && (
          <div className="flex flex-col gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>{result.analysis_basis ?? result.body_region ?? "Assessment"}</span>
                  <UrgencyBadge urgency={mapUrgency(result.urgency)} />
                </CardTitle>
              </CardHeader>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <ListChecks size={18} />
                  Possible Conditions
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col gap-3">
                  {conditions.map((c: any, i: number) => (
                    <div key={i} className="flex items-center justify-between p-3 rounded-md bg-surface-secondary">
                      <div className="flex flex-col gap-1">
                        <span className="text-body-sm font-medium text-text-primary">{c.condition}</span>
                        <span className="text-tiny text-text-secondary">{c.description}</span>
                      </div>
                      <span className="text-body-sm font-bold text-primary ml-4 shrink-0">
                        {c.confidence}%
                      </span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {result.recommended_tests?.length > 0 && (
              <Card>
                <CardHeader><CardTitle>Recommended Tests</CardTitle></CardHeader>
                <CardContent>
                  <ul className="flex flex-col gap-2">
                    {result.recommended_tests.map((t: string, i: number) => (
                      <li key={i} className="flex items-start gap-2 text-body-sm text-text-primary">
                        <span className="text-primary mt-0.5">•</span>{t}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            )}

            {result.suggested_treatment?.length > 0 && (
              <Card>
                <CardHeader><CardTitle>Suggested Treatment</CardTitle></CardHeader>
                <CardContent>
                  <ul className="flex flex-col gap-2">
                    {result.suggested_treatment.map((t: string, i: number) => (
                      <li key={i} className="flex items-start gap-2 text-body-sm text-text-primary">
                        <span className="text-primary mt-0.5">•</span>{t}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            )}

            {result.next_steps?.length > 0 && (
              <Card>
                <CardHeader><CardTitle>Next Steps</CardTitle></CardHeader>
                <CardContent>
                  <ul className="flex flex-col gap-2">
                    {result.next_steps.map((s: string, i: number) => (
                      <li key={i} className="flex items-start gap-2 text-body-sm text-text-primary">
                        <span className="text-primary mt-0.5">•</span>{s}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            )}

            {(result.overall_impression || result.summary) && (
              <Alert>
                <FileText size={16} />
                <p className="text-body-sm text-text-secondary italic mt-1">
                  {result.overall_impression || result.summary}
                </p>
              </Alert>
            )}

            {/* Optional test results refine section */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FlaskConical size={18} />
                  Refine Diagnosis with Test Results
                  <span className="text-tiny font-normal text-text-secondary ml-1">(optional)</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="flex flex-col gap-3">
                <p className="text-body-sm text-text-secondary">
                  If the recommended tests have been carried out, enter the results below in plain English. NexRay AI will narrow down to a confirmed diagnosis.
                </p>
                <Textarea
                  placeholder="e.g. CT scan showed consolidation. Blood culture negative. WBC 14,000..."
                  rows={3}
                  value={testResults}
                  onChange={(e) => setTestResults(e.target.value)}
                />
                <Button
                  variant="outline"
                  onClick={handleRefine}
                  disabled={refineLoading || !testResults.trim()}
                >
                  <FlaskConical size={15} className="mr-2" />
                  {refineLoading ? "Refining..." : "Refine Diagnosis"}
                </Button>
              </CardContent>
            </Card>

            {/* Refined diagnosis results */}
            {refinedDiagnosis && (
              <Card className="border-green-200">
                <CardHeader>
                  <CardTitle className="text-green-700">Refined Diagnosis</CardTitle>
                </CardHeader>
                <CardContent className="flex flex-col gap-4">
                  {refinedDiagnosis.final_diagnosis && (
                    <div className="p-3 rounded-md bg-green-50 border border-green-200">
                      <p className="text-body-sm font-bold text-green-800">
                        Final Diagnosis: {refinedDiagnosis.final_diagnosis}
                      </p>
                    </div>
                  )}

                  {refinedDiagnosis.confirmed_conditions?.length > 0 && (
                    <div className="flex flex-col gap-2">
                      <p className="text-body-sm font-medium text-green-700 flex items-center gap-1">
                        <CheckCircle size={15} /> Confirmed
                      </p>
                      {refinedDiagnosis.confirmed_conditions.map((c: any, i: number) => (
                        <div key={i} className="text-body-sm text-text-primary pl-5">
                          <span className="font-medium">{c.condition}</span>
                          {c.evidence && <span className="text-text-secondary"> — {c.evidence}</span>}
                        </div>
                      ))}
                    </div>
                  )}

                  {refinedDiagnosis.ruled_out?.length > 0 && (
                    <div className="flex flex-col gap-2">
                      <p className="text-body-sm font-medium text-red-600 flex items-center gap-1">
                        <XCircle size={15} /> Ruled Out
                      </p>
                      {refinedDiagnosis.ruled_out.map((r: any, i: number) => (
                        <div key={i} className="text-body-sm text-text-secondary pl-5">
                          <span className="font-medium text-text-primary">{r.condition}</span>
                          {r.reason && <span> — {r.reason}</span>}
                        </div>
                      ))}
                    </div>
                  )}

                  {refinedDiagnosis.summary && (
                    <p className="text-body-sm text-text-secondary italic">{refinedDiagnosis.summary}</p>
                  )}
                </CardContent>
              </Card>
            )}

            <Button onClick={handleDownload} disabled={reportLoading} className="w-full">
              <Download size={16} className="mr-2" />
              {reportLoading ? "Please wait..." : "Download Report"}
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}