# NexRay AI — Frontend

A complete, runnable frontend for NexRay AI: an AI-assisted X-ray analysis and symptom decision-support
platform for clinical staff. Built to the healthcare design system in the brief — Medical Blue / Clinical
Teal palette, Inter typography, 8pt spacing grid, 12–16px radii — with realistic mock data throughout so
every screen is fully navigable ahead of backend integration.

## Run it

```bash
npm install
npm run dev
```

Open http://localhost:5173 — you'll land on `/login`. Any email/password submits (no real auth yet) and
takes you into the app shell at `/dashboard`.

```bash
npm run build     # type-checks and produces a production build in dist/
npm run preview   # serve the production build locally
```

## What's here

**Pages** — Login, Dashboard (stat cards + weekly activity chart + recent analyses + system status),
X-Ray Analysis (region select → drag-and-drop upload → simulated AI processing → findings with confidence
scores, urgency, recommendations), Symptom Checker (patient form → simulated AI assessment keyed off
keywords like fever/chills → likely condition, tests, treatment, next steps), Combined Diagnosis (X-ray +
symptoms merged into one assessment), Reports (search, status filter, pagination, delete, download toast),
Settings (hospital/doctor profile, model & API status).

**Design system** — `tailwind.config.ts` holds every color, radius, shadow, spacing, and type-scale token
from the brief, semantically named. `src/index.css` sets up Inter, focus rings, reduced-motion handling,
and the shimmer keyframe used by loading skeletons.

**Component library** (`src/components/ui`) — Button, Card, Badge, Input, Textarea, Select, Checkbox,
Switch, Tabs, Accordion, Dialog, Drawer, Tooltip, Alert, Table, Pagination, Breadcrumb, Progress, Skeleton,
Empty State — all shadcn/ui-pattern components hand-authored against the clinical palette (the shadcn CLI
itself needs `ui.shadcn.com`, which isn't reachable from the sandbox this was built in, so these are
written to be drop-in compatible with anything you copy in later from there).

**Clinical components** (`src/components/medical`) — ConfidenceMeter, UrgencyBadge, ConditionCard,
StatusChip, PatientSummaryCard, FileUploadCard (react-dropzone), ImageViewer (zoom/pan), AnalysisProgress
(simulated processing animation).

**Layout** — collapsible Sidebar, TopNav (search, notifications, doctor identity), `DashboardLayout` and
`AuthLayout` via React Router's `<Outlet />`.

**Mock data & logic** (`src/lib/mock/data.ts`) — chest/bone/spine findings, a keyword-based symptom
assessment function (e.g. fever + chills/sweats → malaria, per the proposal's Ghana-context conditions),
and a report list with Ghanaian patient names for realism.

## What's intentionally not built yet

This is frontend-only, per your current step. Not included:
- Real backend calls (FastAPI, HuggingFace models, Claude API, ReportLab PDF generation) — the proposal's
  architecture for these is ready to wire up; `src/lib/mock/data.ts` is the seam to replace with real
  `fetch`/React Query calls.
- Real authentication — Login navigates straight through.
- DICOM support in the image viewer — currently standard image formats (PNG/JPG) via `URL.createObjectURL`.
- Actual PDF download — the Reports page shows the interaction (button, toast) without generating a file.

## Tech stack

React 18, TypeScript, Vite, Tailwind CSS, React Router, Radix UI primitives, Recharts, React Hook Form,
React Dropzone, React Hot Toast, Framer Motion, Lucide icons — matching the brief's required stack.
