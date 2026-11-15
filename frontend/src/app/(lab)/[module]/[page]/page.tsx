import { notFound } from "next/navigation";
import { ModulePlaceholder } from "@/components/panels/ModulePlaceholder";
import { MODULES } from "@/lib/modules";

type Props = { params: Promise<{ module: string; page: string }> };

export default async function ModuleSubPage({ params }: Props) {
  const { module: slug, page } = await params;
  const mod = MODULES.find((m) => m.routeSlug === slug);
  if (!mod) notFound();
  const nav = mod.nav.find((n) => n.id === page);
  if (!nav) notFound();
  return (
    <ModulePlaceholder
      title={`${mod.label} · ${nav.label}`}
      description={nav.description ?? mod.description}
    />
  );
}
