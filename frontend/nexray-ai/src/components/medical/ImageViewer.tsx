import { useState } from "react";
import { ZoomIn, ZoomOut, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";

export function ImageViewer({ src, alt }: { src: string; alt: string }) {
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [dragging, setDragging] = useState(false);
  const [start, setStart] = useState({ x: 0, y: 0 });

  return (
    <div className="flex flex-col gap-2">
      <div
        className="relative h-[420px] overflow-hidden rounded-lg border border-border bg-black cursor-grab active:cursor-grabbing"
        onMouseDown={(e) => {
          setDragging(true);
          setStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
        }}
        onMouseMove={(e) => {
          if (!dragging) return;
          setPan({ x: e.clientX - start.x, y: e.clientY - start.y });
        }}
        onMouseUp={() => setDragging(false)}
        onMouseLeave={() => setDragging(false)}
      >
        <img
          src={src}
          alt={alt}
          draggable={false}
          className="absolute top-1/2 left-1/2 max-w-none select-none"
          style={{
            transform: `translate(-50%, -50%) translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
            transition: dragging ? "none" : "transform 120ms ease-out",
          }}
        />
      </div>
      <div className="flex items-center gap-2">
        <Button variant="outline" size="icon" onClick={() => setZoom((z) => Math.min(3, z + 0.25))} aria-label="Zoom in">
          <ZoomIn size={16} />
        </Button>
        <Button variant="outline" size="icon" onClick={() => setZoom((z) => Math.max(0.5, z - 0.25))} aria-label="Zoom out">
          <ZoomOut size={16} />
        </Button>
        <Button
          variant="outline"
          size="icon"
          onClick={() => {
            setZoom(1);
            setPan({ x: 0, y: 0 });
          }}
          aria-label="Reset view"
        >
          <RotateCcw size={16} />
        </Button>
        <span className="text-tiny text-text-secondary ml-1">{Math.round(zoom * 100)}%</span>
      </div>
    </div>
  );
}
