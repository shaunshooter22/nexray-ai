import { Outlet } from "react-router-dom";
import { Activity } from "lucide-react";

export function AuthLayout() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4">
      <div className="w-full max-w-[420px] animate-slide-up">
        <div className="flex flex-col items-center gap-2 mb-8">
          <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary text-white">
            <Activity size={24} />
          </div>
          <p className="text-page-title text-text-primary">NexRay AI</p>
          <p className="text-body-sm text-text-secondary">Clinical decision-support platform</p>
        </div>
        <div className="rounded-lg border border-border bg-surface shadow-md p-8">
          <Outlet />
        </div>
        <p className="text-tiny text-text-secondary text-center mt-6">
          For clinical staff use only. AI outputs assist, but never replace, professional judgment.
        </p>
      </div>
    </div>
  );
}
