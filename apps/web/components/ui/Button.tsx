import { type ButtonHTMLAttributes, forwardRef } from "react";

import { cn } from "@/lib/utils";

type ButtonVariant = "primary" | "secondary" | "ghost";
type ButtonSize = "md" | "lg" | "icon";

const VARIANT_CLASSES: Record<ButtonVariant, string> = {
  primary:
    "bg-indigo-600 text-white hover:bg-indigo-700 disabled:hover:bg-indigo-600 shadow-sm shadow-indigo-600/20",
  secondary:
    "bg-white text-slate-700 border border-slate-300 hover:bg-slate-50 disabled:hover:bg-white",
  ghost: "text-slate-600 hover:bg-slate-100 disabled:hover:bg-transparent",
};

const SIZE_CLASSES: Record<ButtonSize, string> = {
  md: "px-4 py-2 text-sm",
  lg: "px-6 py-3 text-base",
  icon: "h-11 w-11",
};

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: ButtonVariant;
  size?: ButtonSize;
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", size = "md", disabled, ...props }, ref) => {
    return (
      <button
        ref={ref}
        disabled={disabled}
        className={cn(
          "inline-flex items-center justify-center gap-2 rounded-full font-medium transition-colors",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:ring-offset-2",
          "disabled:opacity-50 disabled:cursor-not-allowed",
          VARIANT_CLASSES[variant],
          SIZE_CLASSES[size],
          className,
        )}
        {...props}
      />
    );
  },
);
Button.displayName = "Button";
