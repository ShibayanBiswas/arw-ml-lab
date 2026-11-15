import Image from "next/image";

type Props = { className?: string; priority?: boolean };

export function BrandLogo({ className = "h-10 w-auto", priority }: Props) {
  return (
    <Image
      src="/brand/arwl-logo.png"
      alt="Anand Rathi Wealth"
      width={180}
      height={48}
      className={className}
      priority={priority}
    />
  );
}
