"use client";

import { useEffect, useState } from "react";
import { EvalWorkbench } from "@/components/train/EvalWorkbench";
import { getExperiment, getJob, listSamples, loadSample, startTrain, startTune } from "@/lib/api";

type Props = {
  mode: "recipe" | "leaderboard" | "models" | "detail" | "task" | "cv" | "runs" | "compare";
};

export function TrainWorkbench({ mode }: Props) {
  const [samples, setSamples] = useState<Array<Record<string, unknown>>>([]);
  const [sampleId, setSampleId] = useState("DS3");
  const [target, setTarget] = useState("Survived");
  const [task, setTask] = useState("binary");
  const [tuningPreset, setTuningPreset] = useState<"quick" | "balanced">("quick");
  const [runMode, setRunMode] = useState<"train" | "tune">("train");
  const [status, setStatus] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [board, setBoard] = useState<Array<Record<string, unknown>>>([]);
  const [expId, setExpId] = useState<string | null>(null);
  const [evalPayload, setEvalPayload] = useState<Record<string, unknown> | null>(null);
  const [championKey, setChampionKey] = useState<string | null>(null);
  const [tuneResult, setTuneResult] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    void listSamples()
      .then(setSamples)
      .catch((e) => setError(String(e)));
  }, []);

  async function onRun() {
    setError(null);
    setStatus("Loading sample…");
    try {
      const { job_id } = await loadSample(sampleId);
      let job = await getJob(job_id);
      while (job.status === "queued" || job.status === "running") {
        await new Promise((r) => setTimeout(r, 200));
        job = await getJob(job_id);
      }
      if (job.status !== "done") throw new Error(job.status);
      const datasetId = (job.result as { dataset_id: string }).dataset_id;
      if (runMode === "tune") {
        setStatus(`Tuning (${tuningPreset})…`);
        const started = await startTune({
          dataset_id: datasetId,
          target,
          task,
          algorithm_key: task === "regression" ? "reg.lgbm" : "clf.lgbm",
          preset: tuningPreset,
          n_trials: tuningPreset === "quick" ? 8 : 20,
        });
        setExpId(started.experiment_id);
        let tj = await getJob(started.job_id);
        while (tj.status === "queued" || tj.status === "running") {
          await new Promise((r) => setTimeout(r, 300));
          tj = await getJob(started.job_id);
        }
        if (tj.status !== "done") throw new Error(tj.error || tj.status);
        const exp = await getExperiment(started.experiment_id);
        const tune = ((exp.result || {}) as { tune?: Record<string, unknown> }).tune || null;
        setTuneResult(tune);
        setBoard([]);
        setEvalPayload(null);
        setStatus(`Tune done — best ${String(tune?.best_value ?? "—")}`);
        return;
      }
      setStatus("Training…");
      const started = await startTrain({
        dataset_id: datasetId,
        target,
        task,
        algorithm_keys: [],
        tuning_preset: tuningPreset,
      });
      setExpId(started.experiment_id);
      let tj = await getJob(started.job_id);
      while (tj.status === "queued" || tj.status === "running") {
        await new Promise((r) => setTimeout(r, 300));
        tj = await getJob(started.job_id);
      }
      if (tj.status !== "done") throw new Error(tj.error || tj.status);
      const exp = await getExperiment(started.experiment_id);
      const lb = (exp.leaderboard as Array<Record<string, unknown>>) || [];
      setBoard(lb);
      const result = (exp.result || {}) as {
        eval?: Record<string, unknown>;
        champion?: { algorithm_key?: string };
      };
      setEvalPayload(result.eval || null);
      setChampionKey(result.champion?.algorithm_key || String(lb[0]?.algorithm_key || ""));
      setTuneResult(null);
      setStatus(`Done — ${lb.length} models`);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setStatus("");
    }
  }

  return (
    <div className="space-y-6 p-6">
      <div>
        <p className="section-kicker">
          {mode === "leaderboard" ? "Leaderboard" : mode === "detail" ? "Evaluation" : "Supervised"}
        </p>
        <h1 className="section-title mt-1 text-3xl">
          {mode === "recipe"
            ? "Recipe + Quick train"
            : mode === "leaderboard"
              ? "Leaderboard"
              : mode === "detail"
                ? "Model evaluation"
                : "Models"}
        </h1>
        <p className="mt-2 text-sm text-[var(--fg-muted)]">
          Phase 2-cont-2: recipe + CV catalogue + Optuna Quick/Balanced + Eval Core.
        </p>
        <p
          className="mt-2 text-xs text-[var(--muted)] lg:hidden"
          data-testid="train-desktop-notice"
          data-ux="ST-UX-04"
        >
          Training setup is desktop-first — use a wider viewport for the full recipe and CV controls.
        </p>
      </div>
      {mode !== "leaderboard" || !board.length ? (
        <div className="panel-luxe max-w-xl space-y-3 rounded-2xl p-4">
          <label className="block text-sm">
            Sample
            <select
              className="mt-1 w-full rounded-lg border border-[var(--border)] bg-[var(--bg-elevated)] px-3 py-2"
              value={sampleId}
              onChange={(e) => {
                setSampleId(e.target.value);
                if (e.target.value === "DS3") {
                  setTarget("Survived");
                  setTask("binary");
                }
                if (e.target.value === "DS12") {
                  setTarget("median_house_value");
                  setTask("regression");
                }
              }}
            >
              {samples.map((s) => (
                <option key={String(s.id)} value={String(s.id)}>
                  {String(s.id)} — {String(s.name || s.id)}
                </option>
              ))}
              {!samples.length ? (
                <>
                  <option value="DS3">DS3</option>
                  <option value="DS12">DS12</option>
                </>
              ) : null}
            </select>
          </label>
          <label className="block text-sm">
            Target
            <input
              className="mt-1 w-full rounded-lg border border-[var(--border)] bg-[var(--bg-elevated)] px-3 py-2"
              value={target}
              onChange={(e) => setTarget(e.target.value)}
            />
          </label>
          <label className="block text-sm">
            Task
            <select
              className="mt-1 w-full rounded-lg border border-[var(--border)] bg-[var(--bg-elevated)] px-3 py-2"
              value={task}
              onChange={(e) => setTask(e.target.value)}
            >
              <option value="binary">binary</option>
              <option value="multiclass">multiclass</option>
              <option value="regression">regression</option>
            </select>
          </label>
          <label className="block text-sm">
            Mode
            <select
              className="mt-1 w-full rounded-lg border border-[var(--border)] bg-[var(--bg-elevated)] px-3 py-2"
              value={runMode}
              onChange={(e) => setRunMode(e.target.value as "train" | "tune")}
            >
              <option value="train">Quick train (CV)</option>
              <option value="tune">Optuna tune</option>
            </select>
          </label>
          <label className="block text-sm">
            Tuning preset
            <select
              className="mt-1 w-full rounded-lg border border-[var(--border)] bg-[var(--bg-elevated)] px-3 py-2"
              value={tuningPreset}
              onChange={(e) => setTuningPreset(e.target.value as "quick" | "balanced")}
            >
              <option value="quick">Quick (20 trials)</option>
              <option value="balanced">Balanced (60 trials)</option>
            </select>
          </label>
          <button
            type="button"
            className="rounded-lg gold-gradient px-4 py-2 text-sm font-semibold text-[#111]"
            onClick={() => void onRun()}
          >
            {runMode === "tune" ? `Run Optuna ${tuningPreset}` : "Run Quick train"}
          </button>
        </div>
      ) : null}
      {tuneResult ? (
        <div className="panel-luxe max-w-xl space-y-2 rounded-2xl p-4 font-mono text-xs">
          <p>best_value: {String(tuneResult.best_value)}</p>
          <pre className="overflow-x-auto whitespace-pre-wrap">
            {JSON.stringify(tuneResult.best_params, null, 2)}
          </pre>
        </div>
      ) : null}
      {status ? <p className="text-sm text-[var(--fg-muted)]">{status}</p> : null}
      {error ? (
        <p className="text-sm text-[var(--danger)]" role="alert">
          {error}
        </p>
      ) : null}
      {expId ? <p className="font-mono text-xs text-[var(--fg-subtle)]">experiment {expId}</p> : null}
      {board.length && mode !== "detail" ? (
        <div className="overflow-x-auto rounded-xl border border-[var(--border)]">
          <table className="min-w-full text-left text-sm">
            <thead className="bg-[var(--bg-elevated)] text-[10px] uppercase tracking-wider text-[var(--fg-subtle)]">
              <tr>
                <th className="px-3 py-2">Rank</th>
                <th className="px-3 py-2">Model</th>
                <th className="px-3 py-2">Primary (CV)</th>
                <th className="px-3 py-2">Test</th>
              </tr>
            </thead>
            <tbody>
              {board.map((r) => {
                const primary = String(r.primary_metric);
                const cv = r.cv_mean as Record<string, number>;
                const std = r.cv_std as Record<string, number>;
                const test = r.test as Record<string, number>;
                return (
                  <tr key={String(r.algorithm_key)} className="border-t border-[var(--border)]">
                    <td className="px-3 py-2">{String(r.rank)}</td>
                    <td className="px-3 py-2">{String(r.name)}</td>
                    <td className="px-3 py-2 font-mono text-xs">
                      {cv?.[primary]?.toFixed?.(4)} ± {std?.[primary]?.toFixed?.(4)}
                    </td>
                    <td className="px-3 py-2 font-mono text-xs">{test?.[primary]?.toFixed?.(4)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      ) : null}
      {(mode === "detail" || evalPayload) && (
        <EvalWorkbench
          evalPayload={evalPayload as never}
          championKey={championKey}
        />
      )}
    </div>
  );
}
