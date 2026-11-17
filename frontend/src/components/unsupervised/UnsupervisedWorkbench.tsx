"use client";

import { useMemo, useState } from "react";
import { ArtefactPanel, type ArtefactView } from "@/components/eda/ArtefactPanel";
import {
  runUnsupervised,
  runUnsupervisedAnomalyPlot,
  runUnsupervisedClusteringPlot,
  runUnsupervisedDrPlot,
  type AnomalyCataloguePlot,
  type ClusteringCataloguePlot,
  type DrCataloguePlot,
} from "@/lib/api";

type Mode = "home" | "setup" | "dr" | "clustering" | "anomaly" | "selection" | "profiles" | "compare";

const DEMO_ROWS = Array.from({ length: 40 }, (_, i) => ({
  x: Math.sin(i / 5) + (i % 7) * 0.1,
  y: Math.cos(i / 4) + (i % 5) * 0.15,
  z: i * 0.02,
}));

const ANOMALY_PLOTS: { id: AnomalyCataloguePlot; label: string; artefact: string }[] = [
  { id: "score-hist", label: "Score histogram", artefact: "ANO.P.SCORE_HIST" },
  { id: "ranked", label: "Top-N ranked", artefact: "ANO.P.RANKED" },
  { id: "embed", label: "PCA embed", artefact: "ANO.P.EMBED" },
  { id: "pareto", label: "Pareto rank curve", artefact: "ANO.P.PARETO" },
  { id: "pairwise", label: "Pairwise scatter", artefact: "ANO.P.PAIRWISE" },
];

const CLUSTERING_PLOTS: { id: ClusteringCataloguePlot; label: string; artefact: string }[] = [
  { id: "elbow", label: "Elbow (knee)", artefact: "CLU.P.ELBOW" },
  { id: "silhouette", label: "Silhouette knife", artefact: "CLU.P.SILHOUETTE" },
  { id: "ch", label: "Calinski–Harabasz", artefact: "CLU.P.CH" },
  { id: "db", label: "Davies–Bouldin", artefact: "CLU.P.DB" },
  { id: "gap", label: "Gap statistic", artefact: "CLU.P.GAP" },
  { id: "dendrogram", label: "Dendrogram", artefact: "CLU.P.DENDROGRAM" },
];

const DR_PLOTS: { id: DrCataloguePlot; label: string; artefact: string }[] = [
  { id: "scree", label: "Scree", artefact: "DR.P.SCREE" },
  { id: "cumvar", label: "Cumulative variance", artefact: "DR.P.CUMVAR" },
  { id: "biplot", label: "Biplot", artefact: "DR.P.BIPLOT" },
  { id: "loadings", label: "Loadings heatmap", artefact: "DR.P.LOADINGS" },
  { id: "correlation-circle", label: "Correlation circle", artefact: "DR.P.CORR_CIRCLE" },
  { id: "shepard", label: "Shepard diagram", artefact: "DR.P.SHEPARD" },
];

export function UnsupervisedWorkbench({ mode }: { mode: Mode }) {
  const family =
    mode === "dr" ? "dr" : mode === "anomaly" ? "anomaly" : "clustering";
  const [algorithm, setAlgorithm] = useState(
    family === "dr" ? "pca" : family === "anomaly" ? "isolation_forest" : "kmeans"
  );
  const [status, setStatus] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [plotArtefact, setPlotArtefact] = useState<ArtefactView | null>(null);

  const runBody = useMemo(
    () => ({
      rows: DEMO_ROWS,
      algorithm,
      n_clusters: 3,
      n_components: 2,
      contamination: 0.1,
      seed: 42,
      top_n: 12,
    }),
    [algorithm]
  );

  async function run() {
    setError(null);
    setPlotArtefact(null);
    setStatus(`Running ${family}/${algorithm}…`);
    try {
      const out = await runUnsupervised(family, runBody);
      setResult(out);
      setStatus("Done");
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setStatus("");
    }
  }

  async function runPlot(plot: AnomalyCataloguePlot) {
    setError(null);
    setStatus(`Plot ${plot} (${algorithm})…`);
    try {
      const out = await runUnsupervisedAnomalyPlot(plot, runBody);
      const id = String(out.id ?? "");
      setPlotArtefact({
        id,
        kind: "plot",
        title: id || plot,
        plotly: (out.plotly as Record<string, unknown> | undefined) ?? null,
        numbers: (out.numbers as Record<string, unknown> | undefined) ?? undefined,
      });
      setResult({
        id: out.id,
        algorithm: out.algorithm,
        contamination: out.contamination,
        n_outliers: out.n_outliers,
        seed: out.seed,
        numbers: out.numbers,
      });
      setStatus("Plot ready");
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setStatus("");
    }
  }

  async function runClusterPlot(plot: ClusteringCataloguePlot) {
    setError(null);
    setStatus(`Plot ${plot} (k=${runBody.n_clusters ?? 3})…`);
    try {
      const out = await runUnsupervisedClusteringPlot(plot, runBody);
      const id = String(out.id ?? "");
      setPlotArtefact({
        id,
        kind: "plot",
        title: id || plot,
        plotly: (out.plotly as Record<string, unknown> | undefined) ?? null,
        numbers: (out.numbers as Record<string, unknown> | undefined) ?? undefined,
      });
      setResult({
        id: out.id,
        n_clusters: out.n_clusters ?? runBody.n_clusters,
        seed: out.seed,
        numbers: out.numbers,
      });
      setStatus("Plot ready");
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setStatus("");
    }
  }

  async function runDrPlot(plot: DrCataloguePlot) {
    setError(null);
    setStatus(`Plot ${plot} (${algorithm})…`);
    try {
      const out = await runUnsupervisedDrPlot(plot, runBody);
      const id = String(out.id ?? "");
      setPlotArtefact({
        id,
        kind: "plot",
        title: id || plot,
        plotly: (out.plotly as Record<string, unknown> | undefined) ?? null,
        numbers: (out.numbers as Record<string, unknown> | undefined) ?? undefined,
      });
      setResult({
        id: out.id,
        algorithm: out.algorithm,
        n_components: out.n_components,
        seed: out.seed,
        numbers: out.numbers,
      });
      setStatus("Plot ready");
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setStatus("");
    }
  }

  const algos =
    family === "dr"
      ? ["pca", "svd", "tsne"]
      : family === "anomaly"
        ? ["isolation_forest", "lof"]
        : ["kmeans", "agglomerative"];

  return (
    <div className="space-y-6 p-6">
      <header>
        <h1 className="font-display text-2xl text-[var(--ink)]">Unsupervised · {mode}</h1>
        <p className="mt-1 text-sm text-[var(--muted)]">
          Clustering, DR and anomaly via sklearn/pyod (seed 42). Demo uses a synthetic 40×3 matrix;
          catalogue plots from lab-api (CLU.P.* / DR.P.* / ANO.P.*).
        </p>
      </header>

      <div className="flex flex-wrap items-end gap-3">
        <label className="text-sm">
          Algorithm
          <select
            className="ml-2 border border-[var(--line)] bg-transparent px-2 py-1"
            value={algorithm}
            onChange={(e) => setAlgorithm(e.target.value)}
          >
            {algos.map((a) => (
              <option key={a} value={a}>
                {a}
              </option>
            ))}
          </select>
        </label>
        <button
          type="button"
          className="bg-[var(--gold)] px-3 py-1.5 text-sm text-[var(--ink)]"
          onClick={() => void run()}
        >
          Run fit
        </button>
        {family === "anomaly"
          ? ANOMALY_PLOTS.map((p) => (
              <button
                key={p.id}
                type="button"
                className="border border-[var(--line)] px-3 py-1.5 text-sm"
                title={p.artefact}
                onClick={() => void runPlot(p.id)}
              >
                {p.label}
              </button>
            ))
          : null}
        {family === "clustering"
          ? CLUSTERING_PLOTS.map((p) => (
              <button
                key={p.id}
                type="button"
                className="border border-[var(--line)] px-3 py-1.5 text-sm"
                title={p.artefact}
                onClick={() => void runClusterPlot(p.id)}
              >
                {p.label}
              </button>
            ))
          : null}
        {family === "dr"
          ? DR_PLOTS.map((p) => (
              <button
                key={p.id}
                type="button"
                className="border border-[var(--line)] px-3 py-1.5 text-sm"
                title={p.artefact}
                onClick={() => void runDrPlot(p.id)}
              >
                {p.label}
              </button>
            ))
          : null}
      </div>

      {status && <p className="text-sm text-[var(--muted)]">{status}</p>}
      {error && <p className="text-sm text-red-700">{error}</p>}

      {plotArtefact ? <ArtefactPanel artefact={plotArtefact} /> : null}

      {result && (
        <pre className="max-h-[28rem] overflow-auto border border-[var(--line)] bg-[var(--paper)] p-3 text-xs">
          {JSON.stringify(
            {
              id: result.id,
              algorithm: result.algorithm,
              metrics: result.metrics,
              n_clusters: result.n_clusters,
              n_outliers: result.n_outliers,
              explained_variance_ratio: result.explained_variance_ratio,
              n_components: result.n_components,
              numbers: result.numbers,
            },
            null,
            2
          )}
        </pre>
      )}
    </div>
  );
}