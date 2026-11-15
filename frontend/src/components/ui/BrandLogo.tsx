"use client";

import Image from "next/image";
import { useTheme } from "@/lib/theme";

type Props = {
  className?: string;
  priority?: boolean;
};

/**
 * Theme-aware Anand Rathi Wealth wordmark (SP / Marketing parity).
 * PNG on light; inverted on dark so the mark never disappears.
 */
export function BrandLogo({ className = "h-10 w-auto md:h-11", priority = false }: Props) {
  const { theme } = useTheme();

  return (
    <Image
      src="/brand/arwl-logo.png"
      alt="Anand Rathi Wealth"
      width={240}
      height={54}
      priority={priority}
      className={`${className} object-contain object-left ${
        theme === "dark" ? "brightness-0 invert" : ""
      }`}
    />
  );
}
