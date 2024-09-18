import Loader from "@/components/accessory/loader";

export default function Shimmer() {
  return (
    <div className="h-full w-full animate-pulse">
      <div className="flex h-full w-full flex-col items-center justify-center rounded bg-slate-200 dark:bg-slate-600">
        <Loader />
      </div>
    </div>
  );
}
