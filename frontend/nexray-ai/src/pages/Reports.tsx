// ============================================================
// NexRay AI - Reports Page
// ============================================================

import { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { handleReport, listReports } from "@/lib/api";
import toast from "react-hot-toast";
import { Search, Download, FileText, ScanLine, Stethoscope, GitMerge, User } from "lucide-react";

interface ReportRow {
  id: number;
  session_id: number;
  patient_name: string | null;
  analysis_type: string;
  report_path: string;
  created_at: string;
}

function getTypeIcon(type: string) {
  if (type === "X-Ray Analysis") return <ScanLine size={18} />;
  if (type === "Symptom Check") return <Stethoscope size={18} />;
  if (type === "Combined Case") return <GitMerge size={18} />;
  return <FileText size={18} />;
}

function getTypeBadgeStyle(type: string): string {
  if (type === "X-Ray Analysis") return "bg-blue-100 text-blue-700";
  if (type === "Symptom Check") return "bg-green-100 text-green-700";
  if (type === "Combined Case") return "bg-purple-100 text-purple-700";
  return "bg-gray-100 text-gray-700";
}

export default function Reports() {
  const [reports, setReports] = useState<ReportRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [downloadingId, setDownloadingId] = useState<number | null>(null);

  useEffect(() => {
    fetchReports();
  }, []);

  async function fetchReports() {
    try {
      const data = await listReports();
      setReports(data);
    } catch (err) {
      setReports([]);
    } finally {
      setLoading(false);
    }
  }

  async function handleDownload(reportId: number, patientName: string | null) {
    setDownloadingId(reportId);
    try {
      await handleReport(reportId, patientName ?? undefined);
    } catch (err) {
      toast.error("Failed to get report");
    } finally {
      setDownloadingId(null);
    }
  }

  function formatDate(dateStr: string) {
    try {
      return new Date(dateStr).toLocaleDateString("en-GB", {
        day: "numeric",
        month: "short",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return dateStr;
    }
  }

  const filtered = reports.filter((r) =>
    r.analysis_type.toLowerCase().includes(search.toLowerCase()) ||
    (r.patient_name ?? "").toLowerCase().includes(search.toLowerCase()) ||
    r.session_id.toString().includes(search) ||
    formatDate(r.created_at).toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-page-title text-text-primary">Reports</h1>
        <p className="text-body text-text-secondary mt-1">
          View and download all generated clinical reports.
        </p>
      </div>

      <div className="relative max-w-sm">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-secondary" />
        <Input
          placeholder="Search by patient, type or date..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-9"
        />
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
      ) : filtered.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center gap-3 py-16 text-center">
            <FileText size={32} className="text-text-secondary" />
            <p className="text-card-title text-text-primary">No reports yet</p>
            <p className="text-body-sm text-text-secondary">
              Reports will appear here after you run an analysis.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="flex flex-col gap-3">
          {filtered.map((report) => (
            <Card key={report.id}>
              <CardContent className="flex items-center justify-between gap-4 py-4">
                <div className="flex items-center gap-4">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-primary/10 text-primary">
                    {getTypeIcon(report.analysis_type)}
                  </div>
                  <div className="flex flex-col gap-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <p className="text-body-sm font-medium text-text-primary">
                        {report.analysis_type}
                      </p>
                      <span className={`text-tiny font-medium px-2 py-0.5 rounded-full ${getTypeBadgeStyle(report.analysis_type)}`}>
                        Session #{report.session_id}
                      </span>
                    </div>
                    {report.patient_name && (
                      <p className="text-tiny text-text-secondary flex items-center gap-1">
                        <User size={11} />
                        {report.patient_name}
                      </p>
                    )}
                    <p className="text-tiny text-text-secondary">
                      {formatDate(report.created_at)}
                    </p>
                  </div>
                </div>
                <Button
                  size="sm"
                  onClick={() => handleDownload(report.id, report.patient_name)}
                  disabled={downloadingId === report.id}
                >
                  <Download size={14} className="mr-1" />
                  {downloadingId === report.id ? "..." : "Download"}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}