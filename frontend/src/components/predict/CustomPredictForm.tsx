"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import {
  explainRows,
  getModelSampleRow,
  getModelSchema,
  predictSingle,
  runInsights,
  type FeatureContract,
} from "@/lib/api";

type Props = {
  modelId: string;
};

type Feat = NonNullable<FeatureContract["features"]>[number];

function formFeatures(contract: FeatureContract | null, names: string[]): Feat[] {
  if (!contract?.features) return names.map((n) => ({ name: n, kind: "numeric" }));
  const by = Object.fromEntries(contract.features.map((f) => [f.name, f]));
  return names.map((n) => by[n] ?? { name: n, kind: "numeric" });
}

export function CustomPredictForm({ modelId }: Props) {
  const [contract, setContract] = useState<FeatureContract | null>(null);
  const [featureNames, setFeatureNames] = useState<string[]>([]);
  const [defaults, setDefaults] = useState<Record<string, unknown>>({});
  const [values, setValues] = useState<Record<string, unknown>>({});
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [shap, setShap] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState("");
  const [humilityAction, setHumilityAction] = useState<"warn" | "abstain" | "review">("warn");
  const [narrative, setNarrative] = useState<string | null>(null);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const feats = useMemo(
    () => formFeatures(contract, featureNames),
    [contract, featureNames]
  );

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const [schema, sample] = await Promise.all([
          getModelSchema(modelId),
          getModelSampleRow(modelId),
        ]);
        if (cancelled) return;
        setContract(schema);
        setFeatureNames(sample.feature_names);
        setDefaults(sample.row);
        setValues(sample.row);
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : String(e));
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [modelId]);

  useEffect(() => {
    if (!featureNames.length) return;
    if (timer.current) clearTimeout(timer.current);
    timer.current = setTimeout(() => {
      void (async () => {
        setStatus("Predicting…");
        setError(null);
        try {
          const out = await predictSingle(modelId, values, {
            action_ood: humilityAction,
            action_out_of_range: humilityAction,
            action_wide_interval: humilityAction,
          });
          setResult(out as Record<string, unknown>);
          setStatus("Live");
          try {
            const ex = await explainRows(modelId, [values]);
            setShap(ex);
          } catch {
            setShap(null);
          }
        } catch (e) {
          setError(e instanceof Error ? e.message : String(e));
          setStatus("");
        }
      })();
    }, 300);
    return () => {
      if (timer.current) clearTimeout(timer.current);
    };
  }, [values, modelId, featureNames.length, humilityAction]);

  function setField(name: string, v: unknown) {
    setValues((prev) => ({ ...prev, [name]: v }));
  }

  function resetDefaults() {
    setValues({ ...defaults });
  }

  async function fillRandom() {
    try {
      const sample = await getModelSampleRow(modelId);
      // jitter numerics slightly with deterministic-ish Math from seed-ish
      const row = { ...sample.row };
      for (const f of feats) {
        if (f.kind === "numeric" && typeof row[f.name] === "number") {
          const span = (f.max ?? 1) - (f.min ?? 0) || 1;
          row[f.name] = Number(row[f.name]) + (Math.random() - 0.5) * 0.05 * span;
        }
      }
      setValues(row);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }

  const shapValues = (shap?.shap_values as number[][] | number[] | undefined) ?? null;
  const featureNamesShap = (shap?.feature_names as string[] | undefined) ?? featureNames;

  return (
    <div
      className="min-w-[360px] space-y-4 p-4"
      data-testid="predict-custom-mobile"
      data-ux="ST-UX-04"
    >
      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          className="rounded border border-[var(--border)] px-3 py-1.5 text-sm"
          onClick={resetDefaults}
        >
          Reset defaults
        </button>
        <button
          type="button"
          className="rounded border border-[var(--border)] px-3 py-1.5 text-sm"
          onClick={() => void fillRandom()}
        >
          Fill random row
        </button>
        <label className="flex items-center gap-2 text-sm" title="ST-FEAT-01 humility action">
          Humility
          <select
            className="rounded border border-[var(--border)] bg-transparent px-2 py-1"
            value={humilityAction}
            onChange={(e) =>
              setHumilityAction(e.target.value as "warn" | "abstain" | "review")
            }
          >
            <option value="warn">warn</option>
            <option value="review">review</option>
            <option value="abstain">abstain</option>
          </select>
        </label>
        {status ? <span className="self-center text-sm text-[var(--muted)]">{status}</span> : null}
      </div>
      {error ? <p className="text-sm text-red-600">{error}</p> : null}
      {/* ST-UX-04: form stacks above result ≥360px; side-by-side only from lg */}
      <div className="flex flex-col gap-4 lg:grid lg:grid-cols-2 lg:items-start">
        <div className="grid gap-3 sm:grid-cols-2" data-testid="predict-form-pane">
        {feats.map((f) => {
          if (f.kind === "boolean") {
            return (
              <label key={f.name} className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={Boolean(values[f.name])}
                  onChange={(e) => setField(f.name, e.target.checked)}
                />
                {f.name}
              </label>
            );
          }
          if (f.kind === "categorical") {
            const cats = f.categories ?? [];
            return (
              <label key={f.name} className="block text-sm">
                <span className="text-[var(--muted)]">{f.name}</span>
                <select
                  className="mt-1 w-full rounded border border-[var(--border)] bg-transparent px-2 py-1"
                  value={String(values[f.name] ?? "")}
                  onChange={(e) => setField(f.name, e.target.value)}
                >
                  {cats.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
              </label>
            );
          }
          const min = f.min ?? f.p01 ?? 0;
          const max = f.max ?? f.p99 ?? 100;
          const num = Number(values[f.name] ?? min);
          return (
            <label key={f.name} className="block text-sm">
              <span className="text-[var(--muted)]">{f.name}</span>
              <div className="mt-1 flex gap-2">
                <input
                  type="range"
                  min={min}
                  max={max}
                  step={f.integer ? 1 : (max - min) / 100 || 0.01}
                  value={Number.isFinite(num) ? num : min}
                  onChange={(e) =>
                    setField(f.name, f.integer ? parseInt(e.target.value, 10) : Number(e.target.value))
                  }
                  className="flex-1"
                />
                <input
                  type="number"
                  className="w-24 rounded border border-[var(--border)] bg-transparent px-2 py-1"
                  value={Number.isFinite(num) ? num : ""}
                  onChange={(e) =>
                    setField(
                      f.name,
                      f.integer ? parseInt(e.target.value, 10) : Number(e.target.value)
                    )
                  }
                />
              </div>
            </label>
          );
        })}
        </div>
        <div className="space-y-3" data-testid="predict-result-pane">
      {result ? (
        <div className="rounded border border-[var(--border)] p-3 text-sm" data-artefact="PRED.HUMILITY">
          <p>
            Prediction:{" "}
            <strong>
              {result.prediction == null ? "— (abstained)" : String(result.prediction)}
            </strong>
            {result.refit === false ? " · no refit" : null}
          </p>
          {Array.isArray(result.probabilities) ? (
            <p className="text-[var(--muted)]">
              Probabilities: {(result.probabilities as number[]).map((p) => p.toFixed(4)).join(", ")}
            </p>
          ) : null}
          {result.humility && typeof result.humility === "object" ? (
            <p className="mt-2 text-xs text-[var(--muted)]">
              Humility:{" "}
              {String((result.humility as Record<string, unknown>).humility_action ?? "none")}
              {(result.humility as Record<string, unknown>).abstain
                ? " · prediction suppressed"
                : ""}
              {(result.humility as Record<string, unknown>).needs_human_review
                ? " · needs review"
                : ""}
            </p>
          ) : null}
          <button
            type="button"
            className="mt-2 rounded border border-[var(--border)] px-2 py-1 text-xs hover:bg-[var(--surface-2)]"
            data-artefact="PRED.NARRATIVE"
            onClick={() => {
              void (async () => {
                try {
                  const h =
                    result.humility && typeof result.humility === "object"
                      ? (result.humility as Record<string, unknown>)
                      : {};
                  const out = await runInsights({
                    stage: "prediction",
                    prefer_mock: true,
                    facts: {
                      prediction: result.prediction,
                      probabilities: result.probabilities,
                      humility_action: h.humility_action,
                      abstain: h.abstain,
                      ood_score: h.ood_score,
                      flag_ood: h.flag_ood,
                      flag_out_of_range: h.flag_out_of_range,
                      model_id: modelId,
                    },
                  });
                  const insights = out.insights as Record<string, unknown> | undefined;
                  setNarrative(
                    typeof insights?.summary === "string"
                      ? insights.summary
                      : JSON.stringify(insights ?? out)
                  );
                } catch (e) {
                  setError(e instanceof Error ? e.message : String(e));
                }
              })();
            }}
          >
            Explain this prediction
          </button>
          {narrative ? (
            <p className="mt-2 text-xs text-[var(--muted)]" data-testid="prediction-narrative">
              {narrative}
            </p>
          ) : null}
        </div>
      ) : (
        <div className="rounded border border-dashed border-[var(--border)] p-3 text-sm text-[var(--muted)]">
          Result card appears here (stacks below the form under 1024 px).
        </div>
      )}
      {Array.isArray(shapValues) ? (
        <div className="rounded border border-[var(--border)] p-3 text-sm">
          <p className="mb-2 font-medium">SHAP (local)</p>
          <ul className="space-y-1 font-mono text-xs">
            {(Array.isArray(shapValues[0]) ? (shapValues[0] as number[]) : (shapValues as number[]))
              .map((v, i) => ({ name: featureNamesShap[i] ?? `f${i}`, v }))
              .sort((a, b) => Math.abs(b.v) - Math.abs(a.v))
              .slice(0, 12)
              .map((row) => (
                <li key={row.name}>
                  {row.name}: {row.v.toFixed(4)}
                </li>
              ))}
          </ul>
        </div>
      ) : null}
        </div>
      </div>
    </div>
  );
}
