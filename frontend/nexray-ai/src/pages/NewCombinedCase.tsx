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
  analyze, generateReport, downloadReport, triggerDownload,
  saveAnalysisState, loadAnalysisState, clearAnalysisState
} from "@/lib/api";
import toast from "react-hot-toast";
import { ListChecks, Download, FileText, Stethoscope, User } from "lucide-react";

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
  const [reportLoading, setReportLoading] = useState(false);
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
    setStage("idle");
  }

  function handleFile(f: File) {
    setFile(f);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
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

  async function handleDownloadReport() {
    if (!sessionId) return;
    setReportLoading(true);
    try {
      const reportData = await generateReport(sessionId);
      const blob = await downloadReport(reportData.report_id);
      triggerDownload(blob, `nexray_report_${sessionId}.pdf`);
      toast.success("Report downloaded");
    } catch (err) {
      toast.error("Failed to download report");
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
            <CardHeader>
              <CardTitle>Case Details</CardTitle>
            </CardHeader>
            <CardContent>
              <form className="flex flex-col gap-5" onSubmit={handleSubmit}>

                {/* Patient name */}
                <div className="flex flex-col gap-2">
                  <Label htmlFor="patient_name" className="flex items-center gap-2">
                    <User size={14} />
                    Patient Name
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

            <Button
              onClick={handleDownloadReport}
              disabled={reportLoading}
              className="w-full"
            >
              <Download size={16} className="mr-2" />
              {reportLoading ? "Generating report..." : "Download Report"}
            </Button>

          </div>
        )}
      </div>
    </div>
  );
}