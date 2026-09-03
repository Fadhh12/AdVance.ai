import type { ButtonHTMLAttributes } from "react";

// DESIGN_SYSTEM.md §3: --accent-rec is the primary CTA color (tally light amber).
// One radius, used consistently — not "rounded-full" card-slop.
export function Button({
  className = "",
  variant = "primary",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "primary" | "ghost" }) {
  const base =
    "rounded-md px-4 py-2 text-sm font-medium transition-colors disabled:cursor-not-allowed disabled:opacity-50";
  const variants = {
    primary: "bg-rec text-canvas hover:bg-rec/90",
    ghost: "border border-panel-raised text-ink hover:bg-panel-raised",
  };

  return <button className={`${base} ${variants[variant]} ${className}`} {...props} />;
}
