import { notFound } from "next/navigation";
import { Suspense } from "react";
import { DataWorkbench } from "@/components/data/DataWorkbench";
import { IntakeReview } from "@/components/data/IntakeReview";
import { DeepWorkbench } from "@/components/deep/DeepWorkbench";
import { EdaWorkbench } from "@/components/eda/EdaWorkbench";
import { ExplainWorkbench } from "@/components/explain/ExplainWorkbench";
import { SuitabilityWorkbench } from "@/components/finance/SuitabilityWorkbench";
import { LogicAtlas } from "@/components/learn/LogicAtlas";
import { ModulePlaceholder } from "@/components/panels/ModulePlaceholder";
import { PredictWorkbench } from "@/components/predict/PredictWorkbench";
import { TrainWorkbench } from "@/components/train/TrainWorkbench";
import { TsWorkbench } from "@/components/timeseries/TsWorkbench";
import { UnsupervisedWorkbench } from "@/components/unsupervised/UnsupervisedWorkbench";
import { MODULES } from "@/lib/modules";

type Props = { params: Promise<{ module: string; page: string }> };

export default async function ModuleSubPage({ params }: Props) {
  const { module: slug, page } = await params;
  const mod = MODULES.find((m) => m.routeSlug === slug);
  if (!mod) notFound();
  const nav = mod.nav.find((n) => n.id === page);
  if (!nav) notFound();

  if (slug === "data") {
    if (page === "upload") return <DataWorkbench mode="upload" />;
    if (page === "samples") return <DataWorkbench mode="samples" />;
    if (page === "explorer" || page === "home" || page === "versions")
      return <DataWorkbench mode="explorer" />;
    if (page === "schema") return <DataWorkbench mode="schema" />;
    if (page === "intake-review")
      return (
        <Suspense fallback={<p className="p-6 text-sm">Loading intake…</p>}>
          <IntakeReview />
        </Suspense>
      );
  }
  if (slug === "eda") {
    return <EdaWorkbench section={page} />;
  }
  if (slug === "learn") {
    return <LogicAtlas page={page} />;
  }
  if (slug === "preprocess" && page === "recipe") {
    return <TrainWorkbench mode="recipe" />;
  }
  if (
    slug === "supervised" &&
    (page === "leaderboard" || page === "models" || page === "home" || page === "detail")
  ) {
    const mode =
      page === "leaderboard" ? "leaderboard" : page === "detail" ? "detail" : "models";
    return <TrainWorkbench mode={mode} />;
  }
  if (slug === "predict" && (page === "home" || page === "batch" || page === "single")) {
    const mode = page === "batch" ? "batch" : page === "single" ? "single" : "home";
    return <PredictWorkbench mode={mode} />;
  }
  if (
    slug === "timeseries" &&
    (page === "home" ||
      page === "analysis" ||
      page === "backtesting" ||
      page === "forecast" ||
      page === "lab")
  ) {
    const mode =
      page === "analysis"
        ? "analysis"
        : page === "backtesting"
          ? "backtesting"
          : page === "forecast"
            ? "forecast"
            : page === "lab"
              ? "lab"
              : "home";
    return <TsWorkbench mode={mode} />;
  }
  if (
    slug === "explain" &&
    (page === "home" ||
      page === "global" ||
      page === "local" ||
      page === "interactions" ||
      page === "financial" ||
      page === "compare")
  ) {
    return <ExplainWorkbench mode={page} />;
  }
  if (
    slug === "unsupervised" &&
    (page === "home" ||
      page === "setup" ||
      page === "dr" ||
      page === "clustering" ||
      page === "anomaly" ||
      page === "selection" ||
      page === "profiles" ||
      page === "compare")
  ) {
    return <UnsupervisedWorkbench mode={page} />;
  }
  if (slug === "supervised" && page === "backtest") {
    return <SuitabilityWorkbench />;
  }
  if (slug === "preprocess" && page === "financial") {
    return <SuitabilityWorkbench />;
  }
  if (slug === "supervised" && page === "ensembles") {
    return <DeepWorkbench mode="lab" />;
  }

  return (
    <ModulePlaceholder
      title={`${mod.label} · ${nav.label}`}
      description={nav.description ?? mod.description}
    />
  );
}
