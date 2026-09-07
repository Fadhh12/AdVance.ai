import type { ButtonHTMLAttributes } from "react";

// DESIGN_SYSTEM.md §3: --accent-rec is the primary CTA color (tally light amber).
// One radius, used consistently — not "rounded-full" card-slop. `size` is additive
// (default "md" = the original behavior) so every existing call site stays
// unaffected — added for marketing-page CTAs (§5.5) that need to read as a bigger,
// more confident tap target than in-workspace buttons.
export function Button({
  className = "",
  variant = "primary",
  size = "md",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "ghost";
  size?: "sm" | "md" | "lg";
}) {
  const base =
    "rounded-md font-medium transition-colors disabled:cursor-not-allowed disabled:opacity-50";
  const variants = {
    primary: "bg-rec text-canvas hover:bg-rec/90",
    ghost: "border border-panel-raised text-ink hover:bg-panel-raised",
  };
  const sizes = {
    sm: "px-3 py-1.5 text-xs",
    md: "px-4 py-2 text-sm",
    lg: "px-6 py-3 text-base",
  };

  return (
    <button className={`${base} ${variants[variant]} ${sizes[size]} ${className}`} {...props} />
  );
}
