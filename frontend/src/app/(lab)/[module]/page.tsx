import { notFound } from "next/navigation";
import { ModuleHub } from "@/components/home/ModuleHub";
import { PredictWorkbench } from "@/components/predict/PredictWorkbench";
import { TsWorkbench } from "@/components/timeseries/TsWorkbench";
import { MODULES } from "@/lib/modules";

type Props = { params: Promise<{ module: string }> };

export default async function ModuleHomePage({ params }: Props) {
  const { module: slug } = await params;
  const mod = MODULES.find((m) => m.routeSlug === slug);
  if (!mod) notFound();
  if (slug === "predict") {
    return <PredictWorkbench mode="home" />;
  }
  if (slug === "timeseries") {
    return <TsWorkbench mode="home" />;
  }
  return <ModuleHub mod={mod} />;
}
