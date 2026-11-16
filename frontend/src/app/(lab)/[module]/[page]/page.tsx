import { notFound } from "next/navigation";
import { Suspense } from "react";
import { AdminWorkbench } from "@/components/admin/AdminWorkbench";
import { DataWorkbench } from "@/components/data/DataWorkbench";
import { IntakeReview } from "@/components/data/IntakeReview";
import { DeepWorkbench } from "@/components/deep/DeepWorkbench";
import { EdaWorkbench } from "@/components/eda/EdaWorkbench";
import { ExperimentsWorkbench } from "@/components/experiments/ExperimentsWorkbench";
import { ExplainWorkbench } from "@/components/explain/ExplainWorkbench";
import { SuitabilityWorkbench } from "@/components/finance/SuitabilityWorkbench";
import { LogicAtlas } from "@/components/learn/LogicAtlas";
import { ModulePlaceholder } from "@/components/panels/ModulePlaceholder";
import { PredictWorkbench } from "@/components/predict/PredictWorkbench";
import { ReportsWorkbench } from "@/components/reports/ReportsWorkbench";
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
    if (page === "joins") return <DataWorkbench mode="joins" />;
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
  if (
    slug === "preprocess" &&
    (page === "recipe" ||
      page === "home" ||
      page === "imputation" ||
      page === "encoding" ||
      page === "scaling" ||
      page === "outliers" ||
      page === "features" ||
      page === "selection" ||
      page === "imbalance" ||
      page === "leakage" ||
      page === "preview")
  ) {
    return <TrainWorkbench mode="recipe" />;
  }
  if (
    slug === "supervised" &&
    (page === "leaderboard" ||
      page === "models" ||
      page === "home" ||
      page === "detail" ||
      page === "task" ||
      page === "lab" ||
      page === "cv" ||
      page === "runs" ||
      page === "compare")
  ) {
    const mode =
      page === "leaderboard"
        ? "leaderboard"
        : page === "detail"
          ? "detail"
          : page === "cv"
            ? "cv"
            : page === "runs"
              ? "runs"
              : page === "compare"
                ? "compare"
                : page === "task"
                  ? "task"
                  : "models";
    return <TrainWorkbench mode={mode} />;
  }
  if (
    slug === "predict" &&
    (page === "home" ||
      page === "batch" ||
      page === "single" ||
      page === "what-if" ||
      page === "forecast" ||
      page === "monitoring" ||
      page === "api")
  ) {
    const mode =
      page === "batch"
        ? "batch"
        : page === "single"
          ? "single"
          : page === "what-if"
            ? "what-if"
            : page === "forecast"
              ? "forecast"
              : page === "monitoring"
                ? "monitoring"
                : page === "api"
                  ? "api"
                  : "home";
    return <PredictWorkbench mode={mode} />;
  }
  if (
    slug === "timeseries" &&
    (page === "home" ||
      page === "analysis" ||
      page === "backtesting" ||
      page === "forecast" ||
      page === "lab" ||
      page === "setup" ||
      page === "leaderboard" ||
      page === "residuals" ||
      page === "multivariate")
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
              : page === "setup"
                ? "setup"
                : page === "leaderboard"
                  ? "leaderboard"
                  : page === "residuals"
                    ? "residuals"
                    : page === "multivariate"
                      ? "multivariate"
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
  if (
    slug === "reports" &&
    (page === "home" || page === "builder" || page === "templates" || page === "history")
  ) {
    return <ReportsWorkbench mode={page} />;
  }
  if (
    slug === "experiments" &&
    (page === "home" ||
      page === "runs" ||
      page === "compare" ||
      page === "registry" ||
      page === "lineage" ||
      page === "artifacts")
  ) {
    return <ExperimentsWorkbench mode={page} />;
  }
  if (
    slug === "admin" &&
    (page === "users" ||
      page === "workspaces" ||
      page === "quotas" ||
      page === "workers" ||
      page === "vlm" ||
      page === "audit" ||
      page === "health")
  ) {
    return <AdminWorkbench mode={page} />;
  }

  return (
    <ModulePlaceholder
      title={`${mod.label} · ${nav.label}`}
      description={nav.description ?? mod.description}
    />
  );
}
