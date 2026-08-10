import { Card, CardContent } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import type { PatientInfo } from "@/types/medical";

function initials(name: string) {
  return name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
}

export function PatientSummaryCard({ patient }: { patient: PatientInfo }) {
  return (
    <Card>
      <CardContent className="p-6 flex items-center gap-4">
        <Avatar className="h-12 w-12">
          <AvatarFallback className="text-body">{initials(patient.name)}</AvatarFallback>
        </Avatar>
        <div className="flex-1 min-w-0">
          <p className="text-card-title text-text-primary truncate">{patient.name}</p>
          <p className="text-body-sm text-text-secondary">
            {patient.patientId} · {patient.age} yrs · {patient.gender}
          </p>
          {patient.medicalHistory && (
            <p className="text-tiny text-text-secondary mt-1">History: {patient.medicalHistory}</p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
