"use client";

import { useEffect, useState } from "react";
import { tsAnalysis, tsBacktest, tsHorizon } from "@/lib/api";

type Mode =
  | "home"
  | "analysis"
  | "backtesting"
  | "forecast"
  | "lab"
  | "setup"
  | "leaderboard"
  | "residuals"
  | "multivariate";

export function TsWorkbench({ mode }: { mode: Mode }) {
  const [sampleId, setSampleId] = useState("DS22");
  const [hMax, setHMax] = useState(24);
  const [hDefault, setHDefault] = useState(12);
  const [h, setH] = useState(12);
  const [reasons, setReasons] = useState<string[]>([]);
  const [disabled, setDisabled] = useState<Array<{ model: string; reason: string }>>([]);
  const [status, setStatus] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [backtest, setBacktest] = useState<Record<string, unknown> | null>(null);
  const [analysis, setAnalysis] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const hz = await tsHorizon({ sample_id: sampleId, m: 12, freq: "MS" });
        if (cancelled) return;
        setHMax(hz.h_max);
        setHDefault(hz.h_default);
        setH(Math.min(hz.h_default, hz.h_max));
        setReasons(hz.reasons || []);
        setDisabled(hz.disabled_models || []);
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : String(e));
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [sampleId]);

  async function runBacktest() {
    setError(null);
    setStatus("Running rolling-origin backtest…");
    try {
      const out = await tsBacktest({ sample_id: sampleId, h, w: 4, m: 12, freq: "MS" });
      setBacktest(out);
      setStatus("Backtest done");
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setStatus("");
    }
  }

  async function runAnalysis() {
    setError(null);
    setStatus("Analysing…");
    try {
      const out = await tsAnalysis({ sample_id: sampleId, m: 12 });
      setAnalysis(out);
      setStatus("Analysis done");
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setStatus("");
    }
  }

  async function probeOverMax() {
    setError(null);
    try {
      await tsHorizon({ sample_id: sampleId, h_request: hMax + 1 });
      setStatus("Unexpected: over-max allowed");
    } catch (e) {
      setStatus(`HorizonGuard blocked h>${hMax} (HTTP 422)`);
      setError(e instanceof Error ? e.message.slice(0, 200) : String(e));
    }
  }

  const models = (backtest?.models || {}) as Record<
    string,
    { ok?: boolean; cv_mean?: Record<string, number>; ljung_box?: Record<string, number | string> }
  >;

  return (
    <div className="mx-auto max-w-5xl space-y-4 p-6">
      <header>
        <h1 className="font-display text-2xl tracking-wide">Time Series</h1>
        <p className="mt-1 text-sm text-[var(--muted)]">
          Thin Phase 4 — HorizonGuard (§20), seasonal naive vs airline SARIMA, analysis (STL/ACF).
        </p>
      </header>

      <section className="flex flex-wrap items-end gap-3 rounded border border-[var(--border)] p-3">
        <label className="text-sm">
          Sample
          <select
            className="mt-1 block rounded border border-[var(--border)] bg-transparent px-2 py-1"
            value={sampleId}
            onChange={(e) => setSampleId(e.target.value)}
          >
            <option value="DS22">DS22 Airline (n=144, m=12)</option>
            <option value="DS23">DS23 Shampoo (n=36)</option>
          </select>
        </label>
        <label className="text-sm" title={reasons.join(" · ")}>
          Horizon h (max {hMax})
          <input
            type="range"
            className="mt-1 block w-48"
            min={1}
            max={hMax}
            value={Math.min(h, hMax)}
            onChange={(e) => setH(Number(e.target.value))}
          />
          <span className="ml-2 font-mono text-xs">
            {h} (default {hDefault})
          </span>
        </label>
        {(mode === "backtesting" || mode === "forecast" || mode === "lab" || mode === "home") && (
          <button
            type="button"
            className="rounded bg-[var(--gold)] px-3 py-1.5 text-sm text-black"
            onClick={() => void runBacktest()}
          >
            Run backtest
          </button>
        )}
        {(mode === "analysis" || mode === "home") && (
          <button
            type="button"
            className="rounded border border-[var(--border)] px-3 py-1.5 text-sm"
            onClick={() => void runAnalysis()}
          >
            Run analysis
          </button>
        )}
        <button
          type="button"
          className="rounded border border-[var(--border)] px-3 py-1.5 text-sm"
          onClick={() => void probeOverMax()}
        >
          Probe h&gt;h_max
        </button>
      </section>

      {status ? <p className="text-sm text-[var(--muted)]">{status}</p> : null}
      {error ? <p className="text-sm text-red-600">{error}</p> : null}

      {reasons.length > 0 ? (
        <div className="rounded border border-[var(--border)] p-3 text-xs text-[var(--muted)]">
          <p className="mb-1 font-medium text-[var(--fg)]">HorizonGuard reasons</p>
          <ul className="list-disc pl-5">
            {reasons.slice(0, 8).map((r) => (
              <li key={r}>{r}</li>
            ))}
          </ul>
          {disabled.length > 0 ? (
            <p className="mt-2">
              Disabled: {disabled.map((d) => `${d.model} (${d.reason})`).join("; ")}
            </p>
          ) : null}
        </div>
      ) : null}

      {backtest ? (
        <div className="overflow-x-auto rounded border border-[var(--border)] p-3 text-sm">
          <p className="mb-2 font-medium">
            Backtest W={String(backtest.w)} h={String(backtest.h)}
            {backtest.h_star != null ? ` · h*≈${String(backtest.h_star)}` : ""}
          </p>
          <table className="w-full text-left font-mono text-xs">
            <thead>
              <tr>
                <th className="p-1">Model</th>
                <th className="p-1">MASE</th>
                <th className="p-1">MAE</th>
                <th className="p-1">RMSE</th>
                <th className="p-1">Ljung-Box p</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(models).map(([key, row]) => (
                <tr key={key} className="border-t border-[var(--border)]">
                  <td className="p-1">{key}</td>
                  <td className="p-1">{row.cv_mean?.mase?.toFixed(4) ?? "—"}</td>
                  <td className="p-1">{row.cv_mean?.mae?.toFixed(3) ?? "—"}</td>
                  <td className="p-1">{row.cv_mean?.rmse?.toFixed(3) ?? "—"}</td>
                  <td className="p-1">
                    {typeof row.ljung_box?.pvalue === "number"
                      ? row.ljung_box.pvalue.toFixed(4)
                      : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}

      {analysis ? (
        <div className="rounded border border-[var(--border)] p-3 text-sm">
          <p className="font-medium">Analysis</p>
          <p className="text-[var(--muted)]">
            n={String(analysis.n)} · ACF lags={Array.isArray(analysis.acf) ? analysis.acf.length : 0}
            {analysis.stl && typeof analysis.stl === "object" && "seasonal_strength" in (analysis.stl as object)
              ? ` · STL F_S=${Number((analysis.stl as { seasonal_strength?: number }).seasonal_strength).toFixed(3)}`
              : ""}
          </p>
        </div>
      ) : null}
    </div>
  );
}
