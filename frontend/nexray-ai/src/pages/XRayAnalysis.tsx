// ============================================================
// NexRay AI - X-Ray Analysis Page
// ============================================================

import { useState, useEffect, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { FileUploadCard } from "@/components/medical/FileUploadCard";
import { AnalysisProgress } from "@/components/medical/AnalysisProgress";
import { UrgencyBadge } from "@/components/medical/UrgencyBadge";
import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  analyze, generateReport, handleReport,
  saveAnalysisState, loadAnalysisState, clearAnalysisState
} from "@/lib/api";
import toast from "react-hot-toast";
import { ListChecks, Download, FileText, User } from "lucide-react";

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

export default function XRayAnalysis() {
  const saved = loadAnalysisState();

  const [previewUrl, setPreviewUrl] = useState<string | null>(
    saved?.type === "xray" ? saved?.imageBase64 ?? null : null
  );
  const [patientName, setPatientName] = useState<string>("");
  const [stage, setStage] = useState<Stage>(
    saved?.type === "xray" && saved?.result ? "done" :
    saved?.type === "xray" && saved?.analyzing ? "analyzing" : "idle"
  );
  const [result, setResult] = useState<any>(
    saved?.type === "xray" && saved?.result ? saved.result : null
  );
  const [sessionId, setSessionId] = useState<number | null>(
    saved?.type === "xray" && saved?.sessionId ? saved.sessionId : null
  );
  const [savedPatientName, setSavedPatientName] = useState<string>(
    saved?.type === "xray" ? saved?.patientName ?? "" : ""
  );
  const [reportId, setReportId] = useState<number | null>(null);
  const [reportLoading, setReportLoading] = useState(false);
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (stage === "analyzing") {
      pollingRef.current = setInterval(() => {
        const latest = loadAnalysisState();
        if (latest?.type === "xray" && latest?.result && !latest?.analyzing) {
          setResult(latest.result);
          setSessionId(latest.sessionId);
          setPreviewUrl(latest.imageBase64 ?? null);
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

  function handleNewAnalysis() {
    clearAnalysisState();
    setPreviewUrl(null);
    setPatientName("");
    setResult(null);
    setSessionId(null);
    setSavedPatientName("");
    setReportId(null);
    setStage("idle");
  }

  async function handleFile(f: File) {
    if (!patientName.trim()) {
      toast.error("Please enter the patient's name before uploading");
      return;
    }
    const base64 = await fileToBase64(f);
    setPreviewUrl(base64);
    setResult(null);
    setStage("analyzing");
    saveAnalysisState({
      sessionId: 0,
      result: null,
      type: "xray",
      imageBase64: base64,
      analyzing: true,
      patientName: patientName,
    } as any);
    runAnalysis(f, base64);
  }

  async function runAnalysis(f: File, base64: string) {
    try {
      const data = await analyze(f, undefined, patientName || undefined);
      saveAnalysisState({
        sessionId: data.session_id,
        result: data.analysis,
        type: "xray",
        imageBase64: base64,
        analyzing: false,
        patientName: patientName,
      } as any);
      setResult(data.analysis);
      setSessionId(data.session_id);
      setSavedPatientName(patientName);
      setStage("done");
      toast.success("Analysis complete");
    } catch (err) {
      toast.error("Analysis failed. Please try again.");
      setStage("idle");
      clearAnalysisState();
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

  const conditions = result?.findings || result?.possible_conditions || [];

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-page-title text-text-primary">X-Ray Analysis</h1>
          <p className="text-body text-text-secondary mt-1">
            Upload any X-ray image. NexRay AI will identify the body region and analyse findings automatically.
          </p>
        </div>
        {stage === "done" && (
          <Button variant="outline" onClick={handleNewAnalysis}>
            New Analysis
          </Button>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
        <div className="flex flex-col gap-4">
          {stage === "idle" && (
            <div className="flex flex-col gap-1.5">
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
              <p className="text-tiny text-text-secondary">Required before uploading</p>
            </div>
          )}
          <FileUploadCard onFileAccepted={handleFile} previewUrl={previewUrl} />
          {stage === "analyzing" && <AnalysisProgress />}
          {stage === "done" && savedPatientName && (
            <div className="flex items-center gap-2 text-body-sm text-text-secondary">
              <User size={14} />
              <span>{savedPatientName}</span>
            </div>
          )}
        </div>

        {stage === "done" && result && (
          <div className="flex flex-col gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>Detected Region: {result.body_region}</span>
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
                  {conditions.map((f: any, i: number) => (
                    <div key={i} className="flex items-center justify-between p-3 rounded-md bg-surface-secondary">
                      <div className="flex flex-col gap-1">
                        <span className="text-body-sm font-medium text-text-primary">{f.condition}</span>
                        <span className="text-tiny text-text-secondary">{f.description}</span>
                      </div>
                      <span className="text-body-sm font-bold text-primary ml-4 shrink-0">
                        {f.confidence}%
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

            {result.overall_impression && (
              <Alert>
                <FileText size={16} />
                <p className="text-body-sm text-text-secondary italic mt-1">
                  {result.overall_impression}
                </p>
              </Alert>
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