import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert } from "@/components/ui/alert";
import { UrgencyBadge } from "@/components/medical/UrgencyBadge";
import { ConfidenceMeter } from "@/components/medical/ConfidenceMeter";
import { PatientSummaryCard } from "@/components/medical/PatientSummaryCard";
import { ScanLine, Stethoscope, GitMerge } from "lucide-react";

const patient = {
  name: "Kwabena Mensah",
  patientId: "#2291",
  age: 41,
  gender: "Male" as const,
  medicalHistory: "No known allergies",
};

export default function CombinedDiagnosis() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-page-title text-text-primary">Combined Diagnosis</h1>
        <p className="text-body text-text-secondary mt-1">
          Merge X-ray findings and reported symptoms into a single AI-assisted assessment.
        </p>
      </div>

      <PatientSummaryCard patient={patient} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center gap-2">
            <ScanLine size={18} className="text-primary" />
            <CardTitle>X-Ray findings</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-3">
            <div className="flex items-center justify-between">
              <p className="text-body-sm text-text-primary">Pneumonia (right lower lobe)</p>
              <UrgencyBadge urgency="urgent" />
            </div>
            <ConfidenceMeter confidence={87} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center gap-2">
            <Stethoscope size={18} className="text-secondary" />
            <CardTitle>Reported symptoms</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-3">
            <p className="text-body-sm text-text-secondary">
              Fever (3 days), productive cough, chest pain on breathing, fatigue.
            </p>
            <div className="flex items-center justify-between">
              <p className="text-body-sm text-text-primary">Likely: Pneumonia</p>
              <UrgencyBadge urgency="urgent" />
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center gap-2">
          <GitMerge size={18} className="text-primary" />
          <CardTitle>Combined assessment</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <p className="text-body-sm text-text-secondary">
            X-ray findings and reported symptoms are concordant, both pointing to right lower lobe pneumonia.
            The combination raises overall confidence beyond either signal alone.
          </p>
          <ConfidenceMeter confidence={93} label="Combined confidence" />
          <div className="flex items-center justify-between pt-2 border-t border-border">
            <p className="text-label text-text-primary">Recommended action</p>
            <UrgencyBadge urgency="urgent" />
          </div>
          <p className="text-body-sm text-text-secondary">
            Start empirical antibiotics pending sputum culture, monitor oxygen saturation, and reassess in 48
            hours.
          </p>

          <Alert variant="neutral" title="AI-assisted, not a diagnosis">
            This combined assessment supports — but does not replace — clinical judgment. Confirm before
            initiating treatment.
          </Alert>
        </CardContent>
      </Card>
    </div>
  );
}
