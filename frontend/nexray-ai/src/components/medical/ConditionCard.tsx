import { Card, CardContent } from "@/components/ui/card";
import { ConfidenceMeter } from "./ConfidenceMeter";
import { UrgencyBadge } from "./UrgencyBadge";
import type { ConditionFinding } from "@/types/medical";
import { ClipboardList, Pill } from "lucide-react";

export function ConditionCard({ finding }: { finding: ConditionFinding }) {
  return (
    <Card>
      <CardContent className="p-6 flex flex-col gap-4">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-card-title text-text-primary">{finding.condition}</p>
            <p className="text-body-sm text-text-secondary mt-1">{finding.explanation}</p>
          </div>
          <UrgencyBadge urgency={finding.severity} className="shrink-0" />
        </div>

        <ConfidenceMeter confidence={finding.confidence} />

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2 border-t border-border">
          <div className="flex gap-2">
            <ClipboardList size={16} className="text-text-secondary shrink-0 mt-0.5" />
            <div>
              <p className="text-label text-text-primary">Suggested tests</p>
              <p className="text-body-sm text-text-secondary">{finding.suggestedTests.join(", ")}</p>
            </div>
          </div>
          <div className="flex gap-2">
            <Pill size={16} className="text-text-secondary shrink-0 mt-0.5" />
            <div>
              <p className="text-label text-text-primary">Suggested treatment</p>
              <p className="text-body-sm text-text-secondary">{finding.treatment}</p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
