// ============================================================
// NexRay AI - Symptom Checker Page
// ============================================================

import { useState, useEffect, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";
import { Alert } from "@/components/ui/alert";
import { UrgencyBadge } from "@/components/medical/UrgencyBadge";
import { Stethoscope, ClipboardList, FileText, Download, User, Eye } from "lucide-react";
import {
  analyze, generateReport, openReport, downloadReportFile,
  saveAnalysisState, loadAnalysisState, clearAnalysisState
} from "@/lib/api";
import toast from "react-hot-toast";

type Stage = "idle" | "analyzing" | "done";

function mapUrgency(urgency: string): "routine" | "moderate" | "urgent" | "critical" {
  const map: Record<string, "routine" | "moderate" | "urgent" | "critical"> = {
    "Routine": "routine",
    "Urgent": "urgent",
    "Emergency": "critical",
  };
  return map[urgency] ?? "routine";
}

export default function SymptomChecker() {
  const saved = loadAnalysisState();

  const [symptoms, setSymptoms] = useState("");
  const [patientName, setPatientName] = useState("");
  const [age, setAge] = useState("");
  const [gender, setGender] = useState("female");
  const [duration, setDuration] = useState("");
  const [history, setHistory] = useState("");
  const [stage, setStage] = useState<Stage>(
    saved?.type === "symptoms" && saved?.result ? "done" :
    saved?.type === "symptoms" && saved?.analyzing ? "analyzing" : "idle"
  );
  const [result, setResult] = useState<any>(
    saved?.type === "symptoms" && saved?.result ? saved.result : null
  );
  const [sessionId, setSessionId] = useState<number | null>(
    saved?.type === "symptoms" && saved?.sessionId ? saved.sessionId : null
  );
  const [savedSymptoms, setSavedSymptoms] = useState<string>(
    saved?.type === "symptoms" ? saved?.symptoms ?? "" : ""
  );
  const [savedPatientName, setSavedPatientName] = useState<string>(
    saved?.type === "symptoms" ? saved?.patientName ?? "" : ""
  );
  const [reportId, setReportId] = useState<number | null>(null);
  const [reportLoading, setReportLoading] = useState(false);
  const [downloadLoading, setDownloadLoading] = useState(false);
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (stage === "analyzing") {
      pollingRef.current = setInterval(() => {
        const latest = loadAnalysisState();
        if (latest?.type === "symptoms" && latest?.result && !latest?.analyzing) {
          setResult(latest.result);
          setSessionId(latest.sessionId);
          setSavedSymptoms(latest.symptoms ?? "");
          setSavedPatientName(latest.patientName ?? "");
          setStage("done");
          toast.success("Assessment ready");
          if (pollingRef.current) clearInterval(pollingRef.current);
        }
      }, 1000);
    }
    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current);
    };
  }, [stage]);

  function handleNewCheck() {
    clearAnalysisState();
    setSymptoms("");
    setPatientName("");
    setAge("");
    setGender("female");
    setDuration("");
    setHistory("");
    setResult(null);
    setSessionId(null);
    setSavedSymptoms("");
    setSavedPatientName("");
    setReportId(null);
    setStage("idle");
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!symptoms.trim()) {
      toast.error("Enter symptoms before checking");
      return;
    }

    const fullSymptoms = [
      age ? `Patient age: ${age}` : "",
      gender ? `Gender: ${gender}` : "",
      duration ? `Duration: ${duration}` : "",
      history ? `Medical history: ${history}` : "",
      `Symptoms: ${symptoms}`,
    ].filter(Boolean).join(". ");

    setStage("analyzing");
    setSavedSymptoms(symptoms);
    setSavedPatientName(patientName);
    saveAnalysisState({
      sessionId: 0,
      result: null,
      type: "symptoms",
      symptoms: symptoms,
      patientName: patientName,
      analyzing: true,
    } as any);

    try {
      const data = await analyze(undefined, fullSymptoms, patientName || undefined);
      saveAnalysisState({
        sessionId: data.session_id,
        result: data.analysis,
        type: "symptoms",
        symptoms: symptoms,
        patientName: patientName,
        analyzing: false,
      } as any);
      setResult(data.analysis);
      setSessionId(data.session_id);
      setStage("done");
      toast.success("Assessment ready");
    } catch (err) {
      toast.error("Assessment failed. Please try again.");
      setStage("idle");
      clearAnalysisState();
    }
  }

  async function getOrCreateReport(): Promise<number | null> {
    if (reportId) return reportId;
    if (!sessionId) return null;
    const reportData = await generateReport(sessionId);
    setReportId(reportData.report_id);
    return reportData.report_id;
  }

  async function handleView() {
    setReportLoading(true);
    try {
      const id = await getOrCreateReport();
      if (id) openReport(id);
    } catch (err) {
      toast.error("Failed to open report");
    } finally {
      setReportLoading(false);
    }
  }

  async function handleDownload() {
    setDownloadLoading(true);
    try {
      const id = await getOrCreateReport();
      if (id) await downloadReportFile(id, savedPatientName);
      toast.success("Report downloaded");
    } catch (err) {
      toast.error("Failed to download report");
    } finally {
      setDownloadLoading(false);
    }
  }

  const conditions = result?.possible_conditions || result?.findings || [];

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-page-title text-text-primary">Symptom Checker</h1>
          <p className="text-body text-text-secondary mt-1">
            Enter patient symptoms for an AI-assisted assessment.
          </p>
        </div>
        {stage === "done" && (
          <Button variant="outline" onClick={handleNewCheck}>
            New Check
          </Button>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
        {stage === "idle" && (
          <Card>
            <CardHeader><CardTitle>Patient information</CardTitle></CardHeader>
            <CardContent>
              <form className="flex flex-col gap-4" onSubmit={handleSubmit}>
                <div className="flex flex-col gap-1.5">
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

                <div className="grid grid-cols-2 gap-4">
                  <div className="flex flex-col gap-1.5">
                    <Label htmlFor="age">Age</Label>
                    <Input
                      id="age"
                      type="number"
                      placeholder="e.g. 34"
                      value={age}
                      onChange={(e) => setAge(e.target.value)}
                    />
                  </div>
                  <div className="flex flex-col gap-1.5">
                    <Label>Gender</Label>
                    <Select value={gender} onValueChange={setGender}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="female">Female</SelectItem>
                        <SelectItem value="male">Male</SelectItem>
                        <SelectItem value="other">Other</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="flex flex-col gap-1.5">
                  <Label htmlFor="duration">Symptom duration</Label>
                  <Input
                    id="duration"
                    placeholder="e.g. 3 days"
                    value={duration}
                    onChange={(e) => setDuration(e.target.value)}
                  />
                </div>

                <div className="flex flex-col gap-1.5">
                  <Label htmlFor="history">Medical history (optional)</Label>
                  <Input
                    id="history"
                    placeholder="e.g. hypertension, diabetes"
                    value={history}
                    onChange={(e) => setHistory(e.target.value)}
                  />
                </div>

                <div className="flex flex-col gap-1.5">
                  <Label htmlFor="symptoms">Symptoms</Label>
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
                  Check Symptoms
                </Button>
              </form>
            </CardContent>
          </Card>
        )}

        {stage === "analyzing" && (
          <Card>
            <CardContent className="flex flex-col items-center gap-4 py-12 text-center">
              <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
              <p className="text-card-title text-text-primary">NexRay AI is reviewing the symptoms...</p>
              <p className="text-body-sm text-text-secondary">This usually takes a few seconds.</p>
              {savedSymptoms && (
                <p className="text-tiny text-text-secondary italic">"{savedSymptoms}"</p>
              )}
            </CardContent>
          </Card>
        )}

        {stage === "done" && result && (
          <div className="flex flex-col gap-4">
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

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>Assessment</span>
                  <UrgencyBadge urgency={mapUrgency(result.urgency)} />
                </CardTitle>
              </CardHeader>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <ClipboardList size={18} />
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

            {result.summary && (
              <Alert>
                <FileText size={16} />
                <p className="text-body-sm text-text-secondary italic mt-1">{result.summary}</p>
              </Alert>
            )}

            {/* Two buttons — View and Download */}
            <div className="grid grid-cols-2 gap-3">
              <Button variant="outline" onClick={handleView} disabled={reportLoading}>
                <Eye size={16} className="mr-2" />
                {reportLoading ? "Opening..." : "View Report"}
              </Button>
              <Button onClick={handleDownload} disabled={downloadLoading}>
                <Download size={16} className="mr-2" />
                {downloadLoading ? "Downloading..." : "Download"}
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}