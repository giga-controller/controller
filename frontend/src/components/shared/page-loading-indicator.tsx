import { cn } from "@/lib/utils";
import { Loader2 } from "lucide-react";

export default function PageLoader({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        "flex items-center justify-center h-screen space-x-2",
        className,
      )}
    >
      <Loader2 className="w-30 h-30 text-primary/60 animate-spin" />
      <div className="text-2xl text-muted-foreground">Loading...</div>
    </div>
  );
}
