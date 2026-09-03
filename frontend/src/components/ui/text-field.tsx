import type { InputHTMLAttributes } from "react";

export function TextField({
  label,
  id,
  className = "",
  ...props
}: InputHTMLAttributes<HTMLInputElement> & { label: string }) {
  return (
    <label htmlFor={id} className="flex flex-col gap-1.5 text-sm">
      <span className="text-ink-muted">{label}</span>
      <input
        id={id}
        className={`rounded-md border border-panel-raised bg-panel px-3 py-2 text-ink outline-none focus:border-rec ${className}`}
        {...props}
      />
    </label>
  );
}
