import { notFound } from "next/navigation";
import { ModulePlaceholder } from "@/components/panels/ModulePlaceholder";
import { MODULES } from "@/lib/modules";

type Props = { params: Promise<{ module: string }> };

export default async function ModuleHomePage({ params }: Props) {
  const { module: slug } = await params;
  const mod = MODULES.find((m) => m.routeSlug === slug);
  if (!mod) notFound();
  return <ModulePlaceholder title={mod.label} description={mod.description} />;
}
