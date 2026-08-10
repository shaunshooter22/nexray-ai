import { useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { UploadCloud, ImageIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface FileUploadCardProps {
  onFileAccepted: (file: File) => void;
  previewUrl?: string | null;
  hint?: string;
}

export function FileUploadCard({ onFileAccepted, previewUrl, hint }: FileUploadCardProps) {
  const onDrop = useCallback(
    (accepted: File[]) => {
      if (accepted[0]) onFileAccepted(accepted[0]);
    },
    [onFileAccepted]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "image/png": [], "image/jpeg": [], "image/dicom": [".dcm"] },
    multiple: false,
  });

  if (previewUrl) {
    return (
      <div className="relative rounded-lg border border-border overflow-hidden bg-black/5">
        <img src={previewUrl} alt="Uploaded X-ray preview" className="w-full max-h-[420px] object-contain bg-black" />
        <div {...getRootProps()} className="absolute bottom-3 right-3">
          <input {...getInputProps()} />
          <button
            type="button"
            className="flex items-center gap-2 rounded-md bg-surface/95 border border-border px-3 py-2 text-body-sm text-text-primary shadow-sm hover:bg-surface"
          >
            <ImageIcon size={14} />
            Replace image
          </button>
        </div>
      </div>
    );
  }

  return (
    <div
      {...getRootProps()}
      className={cn(
        "flex flex-col items-center justify-center gap-3 rounded-lg border-2 border-dashed py-16 text-center cursor-pointer transition-colors duration-fast",
        isDragActive ? "border-primary bg-primary/5" : "border-border hover:border-primary/40"
      )}
    >
      <input {...getInputProps()} />
      <div className="flex h-14 w-14 items-center justify-center rounded-full bg-primary/10 text-primary">
        <UploadCloud size={24} />
      </div>
      <p className="text-card-title text-text-primary">
        {isDragActive ? "Drop the X-ray here" : "Drag and drop an X-ray image"}
      </p>
      <p className="text-body-sm text-text-secondary">{hint ?? "or click to browse — DICOM, PNG, JPG supported"}</p>
    </div>
  );
}
