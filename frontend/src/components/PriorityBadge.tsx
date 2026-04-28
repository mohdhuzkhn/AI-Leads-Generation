import clsx from "clsx";

const config: Record<string, { label: string; color: string; bg: string; ring: string }> = {
  A: { label: "A", color: "text-emerald-400", bg: "bg-emerald-500/10", ring: "ring-emerald-500/30" },
  B: { label: "B", color: "text-blue-400",    bg: "bg-blue-500/10",    ring: "ring-blue-500/30"    },
  C: { label: "C", color: "text-amber-400",   bg: "bg-amber-500/10",   ring: "ring-amber-500/30"   },
  D: { label: "D", color: "text-red-400",     bg: "bg-red-500/10",     ring: "ring-red-500/30"     },
};

export default function PriorityBadge({
  priority,
  size = "md",
}: {
  priority: string;
  size?: "sm" | "md" | "lg";
}) {
  const c = config[priority?.toUpperCase()] ?? config["D"];
  return (
    <span
      className={clsx(
        "inline-flex items-center justify-center font-bold rounded-full ring-1",
        c.color, c.bg, c.ring,
        size === "sm" && "w-5 h-5 text-xs",
        size === "md" && "w-7 h-7 text-sm",
        size === "lg" && "w-9 h-9 text-base",
      )}
    >
      {c.label}
    </span>
  );
}
