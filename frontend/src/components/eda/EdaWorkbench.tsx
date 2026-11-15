"use client";

import { useEffect, useMemo, useState } from "react";
import { ArtefactPanel, type ArtefactView } from "@/components/eda/ArtefactPanel";
import { RuleInsightsPanel } from "@/components/insights/RuleInsightsPanel";
import { getEdaByJob, getJob, listDatasets, runEda } from "@/lib/api";

const SECTION_FILTER: Record<string, (id: string, group?: string) => boolean> = {
  overview: (id, g) => id.includes("OVERVIEW") || id.includes("SCHEMA") || g === "quality",
  univariate: (id, g) => g === "univariate_numeric" || g === "univariate_categorical" || id.includes("NUMSUMMARY") || id.includes("CATSUMMARY") || id.includes("NORMALITY") || id.includes("DISTFIT"),
  bivariate: (id, g) => g === "bivariate",
  multivariate: (id, g) => g === "multivariate" || id.includes("CORR") || id.includes("VIF") || id.includes("MI"),
  missingness: (id, g) => g === "missingness" || id.includes("MISSING"),
  outliers: (id, g) => g === "outliers" || id.includes("OUTLIER"),
  target: (id, g) => g === "target" || id.includes("TARGET") || id.includes("WOE") || id.includes("FEAT_TARGET"),
  correlation: (id) => id.includes("CORR") || id.includes("MI") || id.includes("VIF"),
  sequential: (id, g) => g === "sequential" || id.includes("STATION") || id.includes("AUTOCORR") || id.includes("BREAKS") || id.includes("FINSTATS"),
  quality: (id, g) => g === "quality" || id.includes("DUPES") || id.includes("OVERVIEW"),
  report: () => true,
  home: () => true,
};

export function EdaWorkbench({ section }: { section: string }) {
  const [datasets, setDatasets] = useState<Array<Record<string, unknown>>>([]);
  const [datasetId, setDatasetId] = useState<string>("");
  const [artefacts, setArtefacts] = useState<ArtefactView[]>([]);
  const [insights, setInsights] = useState<
    Array<{ rule_id: string; severity: "info" | "warning" | "critical"; message: string; column?: string | null }>
  >([]);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    listDatasets()
      .then((ds) => {
        setDatasets(ds);
        if (ds[0]?.id) setDatasetId(String(ds[0].id));
      })
      .catch((e) => setError(String(e)));
  }, []);

  async function onRun() {
    if (!datasetId) return;
    setStatus("Running EDA…");
    setError("");
    try {
      const { job_id } = await runEda(datasetId);
      let job = await getJob(job_id);
      while (job.status === "queued" || job.status === "running") {
        await new Promise((r) => setTimeout(r, 300));
        job = await getJob(job_id);
      }
      if (job.status !== "done") throw new Error(job.status);
      const eda = await getEdaByJob(job_id);
      setArtefacts(eda.artefacts as ArtefactView[]);
      setInsights(eda.insights);
      setStatus(`Done · ${eda.artefacts.length} artefacts · ${eda.insights.length} insights`);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setStatus("");
    }
  }

  const filter = SECTION_FILTER[section] ?? SECTION_FILTER.home;
  const visible = useMemo(
    () =>
      artefacts.filter((a) => {
        const group = typeof a.numbers?.plot_group === "string" ? a.numbers.plot_group : undefined;
        return filter(a.id, group);
      }),
    [artefacts, filter]
  );

  return (
    <div className="grid gap-4 xl:grid-cols-[1fr_20rem]">
      <div className="space-y-4">
        <section className="panel-stable panel-luxe animate-rise rounded-2xl p-6">
          <p className="section-kicker">EDA</p>
          <h1 className="section-title mt-1 capitalize">{section === "home" ? "Overview workbench" : section}</h1>
          <div className="mt-4 flex flex-wrap items-end gap-3">
            <label className="text-sm">
              Dataset
              <select
                className="mt-1 block rounded-lg border border-[var(--border)] bg-[var(--bg)] px-3 py-2 text-sm"
                value={datasetId}
                onChange={(e) => setDatasetId(e.target.value)}
              >
                {datasets.map((d) => (
                  <option key={String(d.id)} value={String(d.id)}>
                    {String(d.name)} ({String(d.id).slice(0, 8)})
                  </option>
                ))}
              </select>
            </label>
            <button
              type="button"
              className="rounded-lg bg-[var(--gold)] px-4 py-2 text-sm font-medium text-black"
              onClick={() => void onRun()}
            >
              Run EDA
            </button>
          </div>
          {status ? <p className="mt-2 text-sm text-[var(--gold)]">{status}</p> : null}
          {error ? <p className="mt-2 text-sm text-red-600">{error}</p> : null}
        </section>
        <div className="grid gap-4 lg:grid-cols-2">
          {visible.map((a) => (
            <ArtefactPanel key={a.id} artefact={a} />
          ))}
        </div>
      </div>
      <RuleInsightsPanel insights={insights} />
    </div>
  );
}
