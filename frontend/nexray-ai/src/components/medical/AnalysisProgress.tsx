import { useEffect, useState } from "react";
import { Progress } from "@/components/ui/progress";
import { Spinner } from "@/components/ui/spinner-empty-state";

const STEPS = ["Detecting body region", "Running specialist model", "Scoring findings", "Preparing report"];

export function AnalysisProgress({ onComplete }: { onComplete?: () => void }) {
  const [step, setStep] = useState(0);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress((p) => {
        const next = Math.min(100, p + 4);
        if (next === 100) clearInterval(interval);
        return next;
      });
    }, 120);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    setStep(Math.min(STEPS.length - 1, Math.floor((progress / 100) * STEPS.length)));
    if (progress >= 100) onComplete?.();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [progress]);

  return (
    <div className="flex flex-col items-center gap-4 py-12 text-center">
      <Spinner size={28} />
      <p className="text-card-title text-text-primary">{STEPS[step]}…</p>
      <div className="w-full max-w-xs">
        <Progress value={progress} />
      </div>
      <p className="text-tiny text-text-secondary">This usually takes a few seconds</p>
    </div>
  );
}
