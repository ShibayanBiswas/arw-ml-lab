#!/usr/bin/env python3
"""Build prediction-feature sample files for every sample dataset (DS1-DS33).

For each dataset this script writes
  data/samples/predict/<name>_predict.csv        - rows to send to Prediction Studio (target removed)
  data/samples/predict/contracts/<name>.feature_contract.json
                                                 - the feature contract a model trained on the
                                                   *training* part would save (ARCHITECTURE §45.2)
and a summary data/samples/predict/predict_manifest.json.

Rules (ARCHITECTURE §45.9):
  * seed 42 everywhere;
  * non-sequential data: shuffle with numpy default_rng(42); the last 20 % is the hold-out;
    30 rows are drawn from the hold-out (fewer if the hold-out is smaller);
  * sequential / time-series data: chronological split; the request rows are the last rows
    (future timestamps for forecasting, capped by HorizonGuard §20);
  * the target column (and leakage columns such as casual/registered for bike sharing) is removed;
  * lazy datasets are downloaded into a cache (default .cache/predict_samples, git-ignored);
    if a download is impossible the file is generated schema-correct and marked "synthetic".

Usage: python scripts/make_predict_samples.py [--cache-dir DIR] [--offline]
Requires: pandas, numpy, scikit-learn, openpyxl, python-calamine, pyarrow (all pinned in backend/requirements).
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "data" / "samples"
OUT = SAMPLES / "predict"
UA = {"User-Agent": "Mozilla/5.0 (ARW ML Lab sample builder)"}


# ----------------------------------------------------------------------------- helpers
def fetch(url: str, cache: Path, name: str, offline: bool) -> Path | None:
    cache.mkdir(parents=True, exist_ok=True)
    p = cache / name
    if p.exists() and p.stat().st_size > 0:
        return p
    if offline:
        return None
    from labcore.ops.egress_allowlist import check_egress_url

    check_egress_url(url)
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=180) as r:
            p.write_bytes(r.read())
        return p
    except Exception as exc:  # network failure -> synthetic fallback
        print(f"  ! download failed for {url}: {exc}")
        return None


def read_arff(path: Path) -> pd.DataFrame:
    """Minimal ARFF reader (numeric, nominal and string attributes)."""
    cols, rows, data = [], [], False
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        s = line.strip()
        if not s or s.startswith("%"):
            continue
        if not data:
            low = s.lower()
            if low.startswith("@attribute"):
                rest = s[len("@attribute"):].strip()
                if rest.startswith("'"):
                    name = rest[1:rest.index("'", 1)]
                elif rest.startswith('"'):
                    name = rest[1:rest.index('"', 1)]
                else:
                    name = rest.split()[0]
                cols.append(name)
            elif low.startswith("@data"):
                data = True
            continue
        rows.append(next(csv.reader([s], quotechar="'", skipinitialspace=True)))
    df = pd.DataFrame(rows, columns=cols).replace("?", np.nan)
    for c in df.columns:
        conv = pd.to_numeric(df[c], errors="coerce")
        if conv.notna().sum() == df[c].notna().sum():
            df[c] = conv
    return df


def holdout_rows(df: pd.DataFrame, n: int = 30) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(SEED)
    idx = rng.permutation(len(df))
    cut = int(round(len(df) * 0.8))
    train, hold = df.iloc[idx[:cut]], df.iloc[idx[cut:]]
    take = hold.iloc[: min(n, len(hold))].sort_index()
    return train, take


def tail_rows(df: pd.DataFrame, n: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    return df.iloc[: len(df) - n], df.iloc[len(df) - n:]


def contract(train: pd.DataFrame, features: list[str], *, ds: str, task: str, target: str | None,
             id_cols: list[str] | None = None, time_col: str | None = None, freq: str | None = None,
             horizon: int | None = None, series_col: str | None = None) -> dict:
    feats = []
    for c in features:
        s = train[c]
        entry: dict = {"name": c, "nullable": bool(s.isna().any())}
        if pd.api.types.is_bool_dtype(s):
            entry.update(kind="boolean", dtype="bool")
        elif pd.api.types.is_numeric_dtype(s):
            q = s.dropna().astype(float)
            entry.update(kind="numeric", dtype=str(s.dtype),
                         min=float(q.min()) if len(q) else None, max=float(q.max()) if len(q) else None,
                         median=float(q.median()) if len(q) else None,
                         p01=float(q.quantile(0.01)) if len(q) else None, p99=float(q.quantile(0.99)) if len(q) else None,
                         integer=bool(len(q) and np.all(np.mod(q, 1) == 0)))
        elif c == time_col or pd.api.types.is_datetime64_any_dtype(s):
            d = pd.to_datetime(s, errors="coerce")
            entry.update(kind="datetime", dtype="datetime64[ns]", min=str(d.min()), max=str(d.max()))
        else:
            vc = s.dropna().astype(str).value_counts()
            if len(vc) > 50 and len(vc) > 0.5 * s.notna().sum():
                # identifier-like / free text (e.g. names, tickets): never store the values (PII), §45.2
                entry.update(kind="identifier_like", dtype="string", n_categories=int(len(vc)),
                             role="excluded_by_default", categories=None, mode=None)
            else:
                entry.update(kind="categorical", dtype="string", categories=sorted(vc.index.tolist())[:200],
                             n_categories=int(len(vc)), mode=str(vc.index[0]) if len(vc) else None,
                             categories_truncated=bool(len(vc) > 200))
        feats.append(entry)
    return {
        "contract_version": "1.0", "dataset_id": ds, "task": task, "target": target,
        "features": feats, "id_columns": id_cols or [], "time_column": time_col, "frequency": freq,
        "series_column": series_col, "horizon_max": horizon, "seed": SEED,
        "n_train_rows": int(len(train)),
        "note": "illustrative contract computed from the training split of the sample; the real one is "
                "saved by the training job (ARCHITECTURE §45.2)",
    }


# ----------------------------------------------------------------------------- builders
RESULTS: list[dict] = []


def emit(ds: str, name: str, df_out: pd.DataFrame, con: dict, source: str, note: str, split: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "contracts").mkdir(exist_ok=True)
    f = OUT / f"{name}_predict.csv"
    df_out.to_csv(f, index=False)
    (OUT / "contracts" / f"{name}.feature_contract.json").write_text(json.dumps(con, indent=1, default=str))
    RESULTS.append({"id": ds, "name": name, "file": f"data/samples/predict/{f.name}",
                    "contract": f"data/samples/predict/contracts/{name}.feature_contract.json",
                    "rows": int(len(df_out)), "columns": list(map(str, df_out.columns)), "task": con["task"],
                    "target_removed": con["target"], "split": split, "source": source, "note": note})
    print(f"  {ds:5s} {name:28s} rows={len(df_out):3d} cols={df_out.shape[1]:3d} source={source}")


def tabular(ds, name, df, target, task, *, drop=(), id_cols=(), source="bundled", note=""):
    df = df.reset_index(drop=True)
    train, take = holdout_rows(df)
    feats = [c for c in df.columns if c not in (target, *drop, *id_cols)]
    out = take[[*id_cols, *feats]]
    emit(ds, name, out, contract(train, feats, ds=ds, task=task, target=target, id_cols=list(id_cols)),
         source, note, "random 80/20 hold-out (seed 42), 30 hold-out rows")


def unsup(ds, name, df, task, *, id_cols=(), source="bundled", note=""):
    tabular(ds, name, df, None, task, id_cols=id_cols, source=source, note=note)


def forecast(ds, name, df, time_col, target, freq, h, *, exog=(), source="bundled", note=""):
    train, fut = tail_rows(df.reset_index(drop=True), h)
    out = fut[[time_col, *exog]]
    con = contract(train, [time_col, *exog], ds=ds, task="forecast", target=target, time_col=time_col,
                   freq=freq, horizon=h)
    emit(ds, name, out, con, source, note, f"chronological; last {h} timestamps = forecast request (h = HorizonGuard cap)")


def sequential(ds, name, df, time_col, target, task, n=30, *, drop=(), source="bundled", note=""):
    train, take = tail_rows(df.reset_index(drop=True), n)
    feats = [c for c in df.columns if c not in (target, *drop)]
    emit(ds, name, take[feats], contract(train, feats, ds=ds, task=task, target=target, time_col=time_col),
         source, note, f"chronological; last {n} rows (no shuffling)")


def synth_rng():
    return np.random.default_rng(SEED)


# ----------------------------------------------------------------------------- main
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache-dir", default=str(ROOT / ".cache" / "predict_samples"))
    ap.add_argument("--offline", action="store_true", help="never download; use cache or synthetic rows")
    a = ap.parse_args()
    cache, off = Path(a.cache_dir), a.offline
    S = SAMPLES

    # --- bundled supervised -------------------------------------------------------------
    iris = pd.read_csv(S / "iris.data", header=None,
                       names=["sepal_length", "sepal_width", "petal_length", "petal_width", "class"]).dropna()
    tabular("DS1", "iris", iris, "class", "multiclass")

    wd = pd.read_csv(S / "breast_cancer_wdbc.data", header=None)
    base = ["radius", "texture", "perimeter", "area", "smoothness", "compactness", "concavity",
            "concave_points", "symmetry", "fractal_dimension"]
    wd.columns = ["id", "diagnosis"] + [f"{b}_{s}" for s in ("mean", "se", "worst") for b in base]
    tabular("DS2", "breast_cancer_wdbc", wd, "diagnosis", "binary", id_cols=("id",))

    ti = pd.read_csv(S / "titanic.csv")
    tabular("DS3", "titanic", ti, "Survived", "binary", id_cols=("PassengerId",))

    # DS4 Adult: official test file = real hold-out
    p = fetch("https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.test", cache, "adult.test", off)
    cols = ["age", "workclass", "fnlwgt", "education", "education_num", "marital_status", "occupation",
            "relationship", "race", "sex", "capital_gain", "capital_loss", "hours_per_week", "native_country", "income"]
    ptr = fetch("https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.data", cache, "adult.data", off)
    if p and ptr:
        tr = pd.read_csv(ptr, header=None, names=cols, skipinitialspace=True, na_values="?")
        te = pd.read_csv(p, header=None, names=cols, skipinitialspace=True, na_values="?", skiprows=1)
        take = te.iloc[np.sort(np.random.default_rng(SEED).choice(len(te), 30, replace=False))]
        feats = cols[:-1]
        emit("DS4", "adult", take[feats], contract(tr, feats, ds="DS4", task="binary", target="income"),
             "downloaded (UCI adult.test)", "rows from the official adult.test hold-out", "official test file, 30 rows (seed 42)")
    else:
        synth_fail("DS4", "adult")

    p = fetch("https://openml.org/data/v1/download/31/credit-g.arff", cache, "credit-g.arff", off)
    tabular("DS5", "german_credit", read_arff(p), "class", "binary", source="downloaded (OpenML 31)") if p else synth_fail("DS5", "german_credit")

    p = fetch("https://data.openml.org/datasets/0000/1597/dataset_1597.pq", cache, "creditcard.pq", off)
    if p:
        cc = pd.read_parquet(p)
        tabular("DS6", "credit_card_fraud", cc, "Class", "binary", source="downloaded (OpenML 1597 parquet)",
                note="supervised view; hold-out rows mostly class 0 because of the 0.17% prevalence")
        unsup("DS21", "credit_card_fraud_unlabelled", cc.drop(columns=["Class"]), "anomaly_detection",
              source="downloaded (OpenML 1597 parquet)", note="labels hidden; same hold-out rule")
    else:
        synth_fail("DS6", "credit_card_fraud"); synth_fail("DS21", "credit_card_fraud_unlabelled")

    p = fetch("https://archive.ics.uci.edu/static/public/222/bank+marketing.zip", cache, "bank_marketing.zip", off)
    if p:
        with zipfile.ZipFile(p) as z:
            inner = zipfile.ZipFile(io.BytesIO(z.read("bank.zip")))
            bank = pd.read_csv(io.BytesIO(inner.read("bank-full.csv")), sep=";")
        tabular("DS7", "bank_marketing", bank, "y", "binary", drop=("duration",), source="downloaded (UCI 222)",
                note="'duration' removed: known only after the call (leakage)")
    else:
        synth_fail("DS7", "bank_marketing")

    p = fetch("https://archive.ics.uci.edu/static/public/350/default+of+credit+card+clients.zip", cache, "credit_default.zip", off)
    if p:
        with zipfile.ZipFile(p) as z:
            xls = [n for n in z.namelist() if n.endswith(".xls")][0]
            cd = pd.read_excel(io.BytesIO(z.read(xls)), header=1, engine="calamine")
        tabular("DS8", "credit_default_taiwan", cd, "default payment next month", "binary", id_cols=("ID",),
                source="downloaded (UCI 350)")
    else:
        synth_fail("DS8", "credit_default_taiwan")

    hd = pd.read_csv(S / "heart_disease" / "processed.cleveland.data", header=None, na_values="?",
                     names=["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", "thalach", "exang",
                            "oldpeak", "slope", "ca", "thal", "num"])
    tabular("DS9", "heart_disease_cleveland", hd, "num", "binary")

    tabular("DS10", "penguins", pd.read_csv(S / "penguins.csv"), "species", "multiclass")
    tabular("DS11", "wine_quality_red", pd.read_csv(S / "wine_quality_red.csv", sep=";"), "quality", "regression")

    p = fetch("https://openml.org/data/v1/download/52649/houses.arff", cache, "houses.arff", off)
    tabular("DS12", "california_housing", read_arff(p), "median_house_value", "regression",
            source="downloaded (OpenML 537)") if p else synth_fail("DS12", "california_housing")

    p = fetch("https://openml.org/data/v1/download/21754539/house_prices.arff", cache, "house_prices.arff", off)
    tabular("DS13", "ames_house_prices", read_arff(p), "SalePrice", "regression", id_cols=("Id",),
            source="downloaded (OpenML 42165)") if p else synth_fail("DS13", "ames_house_prices")

    am = pd.read_csv(S / "auto_mpg" / "auto-mpg.data", sep=r"\s+", header=None, na_values="?",
                     names=["mpg", "cylinders", "displacement", "horsepower", "weight", "acceleration",
                            "model_year", "origin", "car_name"])
    tabular("DS14", "auto_mpg", am, "mpg", "regression", id_cols=("car_name",))

    co = pd.read_excel(S / "concrete" / "Concrete_Data.xls", engine="calamine")
    co.columns = [c.split("(")[0].strip() for c in co.columns]
    tabular("DS15", "concrete_strength", co, "Concrete compressive strength", "regression")

    bk = pd.read_csv(S / "bike_sharing" / "day.csv")
    sequential("DS16", "bike_sharing_day", bk, "dteday", "cnt", "regression",
               drop=("instant", "casual", "registered"),
               note="casual + registered = cnt, removed as leakage; chronological hold-out")

    # DS17 sklearn built-ins (three files)
    from sklearn import datasets as skd
    for nm, loader, task in (("diabetes", skd.load_diabetes, "regression"),
                             ("digits", skd.load_digits, "multiclass"),
                             ("wine", skd.load_wine, "multiclass")):
        b = loader(as_frame=True)
        tabular("DS17", f"sklearn_{nm}", b.frame, b.target.name, task, source="bundled with scikit-learn")

    unsup("DS18", "mall_customers", pd.read_csv(S / "mall_customers.csv", dtype={"CustomerID": str}),
          "clustering", id_cols=("CustomerID",))
    unsup("DS19", "wholesale_customers", pd.read_csv(S / "wholesale_customers.csv"), "clustering+anomaly")

    # DS20 Online Retail II -> RFM per customer
    p = fetch("https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip", cache, "online_retail_ii.zip", off)
    if p:
        rfm_path = cache / "online_retail_rfm.parquet"
        if not rfm_path.exists():
            with zipfile.ZipFile(p) as z:
                xl = [n for n in z.namelist() if n.endswith(".xlsx")][0]
                frames = pd.read_excel(io.BytesIO(z.read(xl)), sheet_name=None)
            tx = pd.concat(frames.values(), ignore_index=True).dropna(subset=["Customer ID"])
            tx = tx[(tx["Quantity"] > 0) & (tx["Price"] > 0)]
            tx["amount"] = tx["Quantity"] * tx["Price"]
            snap = tx["InvoiceDate"].max() + pd.Timedelta(days=1)
            rfm = tx.groupby("Customer ID").agg(recency_days=("InvoiceDate", lambda d: (snap - d.max()).days),
                                                frequency=("Invoice", "nunique"), monetary=("amount", "sum"),
                                                country=("Country", "first")).reset_index()
            rfm["Customer ID"] = rfm["Customer ID"].astype(int).astype(str)
            rfm.to_parquet(rfm_path)
        unsup("DS20", "online_retail_rfm", pd.read_parquet(rfm_path), "clustering", id_cols=("Customer ID",),
              source="downloaded (UCI 502), RFM derived", note="one row per customer: recency, frequency, monetary, country")
    else:
        synth_fail("DS20", "online_retail_rfm")

    # --- time series ----------------------------------------------------------------------
    forecast("DS22", "airline_passengers", pd.read_csv(S / "airline_passengers.csv"), "Month", "Passengers", "MS", 24)
    sh = pd.read_csv(S / "shampoo.csv")
    sh["Month"] = [f"{2000 + int(m.split('-')[0]):04d}-{m.split('-')[1]}" for m in sh["Month"]]
    forecast("DS23", "shampoo_sales", sh, "Month", "Sales", "MS", 9,
             note="n = 36 < 50 so HorizonGuard caps h at floor(36/4) = 9; year index mapped to 2001-2003")
    forecast("DS24", "daily_min_temperatures", pd.read_csv(S / "daily_min_temperatures.csv"), "Date", "Temp", "D", 30)
    forecast("DS25", "monthly_sunspots", pd.read_csv(S / "monthly_sunspots.csv"), "Month", "Sunspots", "MS", 24)
    co2 = pd.read_csv(S / "co2_mauna_loa.csv", comment="#")
    co2["date"] = pd.to_datetime(dict(year=co2["year"], month=co2["month"], day=1)).dt.strftime("%Y-%m-%d")
    forecast("DS26", "co2_mauna_loa", co2[["date", "average"]], "date", "average", "MS", 24)
    md = pd.read_csv(S / "statsmodels_macrodata.csv")
    md["date"] = pd.PeriodIndex.from_fields(year=md["year"], quarter=md["quarter"], freq="Q").to_timestamp().strftime("%Y-%m-%d")
    forecast("DS27", "us_macrodata", md, "date", "realgdp", "QS", 16,
             exog=("realcons", "realinv", "realgovt", "realdpi", "cpi", "m1", "tbilrate", "unemp", "pop"),
             note="quarterly hard cap 16; exogenous columns are scenario values for an ARIMAX/VARX model")
    et = pd.read_csv(S / "etth1.csv")
    forecast("DS28", "etth1", et, "date", "OT", "h", 48,
             exog=("HUFL", "HULL", "MUFL", "MULL", "LUFL", "LULL"), note="known-future exogenous loads for 48 h")

    # DS29 Electricity: request rows need only series ids and future timestamps (schema-derived)
    ts = pd.date_range("2015-01-01 00:00", periods=24, freq="h")
    el = pd.DataFrame([(u, t.strftime("%Y-%m-%d %H:%M:%S")) for u in ("MT_001", "MT_002") for t in ts],
                      columns=["unique_id", "ds"])
    emit("DS29", "electricity_load", el,
         {"contract_version": "1.0", "dataset_id": "DS29", "task": "forecast_global", "target": "y (kW, hourly sum of 15-min readings)",
          "features": [{"name": "unique_id", "kind": "categorical", "dtype": "string",
                        "categories": [f"MT_{i:03d}" for i in range(1, 371)], "n_categories": 370, "mode": "MT_001"},
                       {"name": "ds", "kind": "datetime", "dtype": "datetime64[ns]", "min": "2011-01-01", "max": "2014-12-31 23:00:00"}],
          "id_columns": [], "time_column": "ds", "series_column": "unique_id", "frequency": "h", "horizon_max": 168,
          "seed": SEED, "n_train_rows": None,
          "note": "schema-derived from the UCI 321 description (370 clients MT_001..MT_370, 2011-2014); the 260 MB archive is not downloaded"},
         "schema-derived (no download)", "2 clients x next 24 hours after the end of the data", "future timestamps, h = 24")

    nf = pd.read_csv(S / "nifty50_daily_5y.csv")
    sequential("DS30", "nifty50_daily", nf, "date", None, "triple_barrier / returns",
               note="target is derived (forward return / triple-barrier label) so no column is removed; last 30 trading days")

    # DS31 multi-asset (Yahoo chart API)
    frames = []
    for sym in ("^GSPC", "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS"):
        p = fetch(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range=3mo&interval=1d",
                  cache, f"yahoo_{sym.replace('^', '')}.json", off)
        if not p:
            continue
        r = json.loads(p.read_text())["chart"]["result"][0]
        q = r["indicators"]["quote"][0]
        frames.append(pd.DataFrame({"symbol": sym,
                                    "date": pd.to_datetime(r["timestamp"], unit="s").strftime("%Y-%m-%d"),
                                    "open": q["open"], "high": q["high"], "low": q["low"],
                                    "close": q["close"], "volume": q["volume"]}).dropna())
    if frames:
        mk = pd.concat(frames)
        mk_train = mk.groupby("symbol").head(len(mk))  # all history is "train" for the contract
        take = mk.groupby("symbol").tail(6).reset_index(drop=True)
        emit("DS31", "multi_asset_prices", take,
             contract(mk_train, list(take.columns), ds="DS31", task="portfolio / sequential", target=None,
                      time_col="date", series_col="symbol"),
             "downloaded (Yahoo chart API, 3 months)", "^GSPC + 4 NIFTY constituents, last 6 trading days each",
             "chronological; last 6 rows per symbol")
    else:
        synth_fail("DS31", "multi_asset_prices")

    # DS32 TradingLab dollar bars: private repository -> synthetic, schema-correct
    rng = synth_rng()
    n = 30
    t0 = pd.Timestamp("2026-11-02 09:15:00")
    times = t0 + pd.to_timedelta(np.cumsum(rng.integers(20, 240, n)), unit="s")
    close = 1300 * np.exp(np.cumsum(rng.normal(0, 0.0015, n)))
    open_ = np.r_[1300, close[:-1]]
    high = np.maximum(open_, close) * (1 + rng.uniform(0, 0.001, n))
    low = np.minimum(open_, close) * (1 - rng.uniform(0, 0.001, n))
    vol = rng.integers(500, 5000, n)
    db = pd.DataFrame({"date_time": times.strftime("%Y-%m-%d %H:%M:%S"), "open": open_.round(2), "high": high.round(2),
                       "low": low.round(2), "close": close.round(2), "cum_vol": vol, "cum_dollar": (vol * close).round(2),
                       "cum_ticks": rng.integers(50, 400, n)})
    emit("DS32", "tradinglab_dollar_bars", db,
         contract(db, list(db.columns), ds="DS32", task="labeling / sequential", target=None, time_col="date_time"),
         "synthetic (schema-correct)",
         "TradingLab is a private repository and is not shipped; columns follow its dollar-bar sample "
         "(date_time, open, high, low, close, cum_vol, cum_dollar, cum_ticks); values are a seeded random walk",
         "synthetic, 30 bars")

    # DS33 synthetic generator (make_classification) - the dataset itself is synthetic
    from sklearn.datasets import make_classification
    X, y = make_classification(n_samples=1000, n_features=10, n_informative=5, n_redundant=3, random_state=SEED)
    sy = pd.DataFrame(X, columns=[f"I_{i}" for i in range(5)] + [f"R_{i}" for i in range(3)] + [f"N_{i}" for i in range(2)])
    sy["target"] = y
    tabular("DS33", "synthetic_classification", sy, "target", "binary", source="synthetic generator (by design)",
            note="make_classification(n=1000, 5 informative, 3 redundant, 2 noise, random_state=42)")

    RESULTS.sort(key=lambda r: (int(r["id"][2:]), r["name"]))
    (OUT / "predict_manifest.json").write_text(json.dumps(
        {"seed": SEED, "generated_by": "scripts/make_predict_samples.py", "files": RESULTS}, indent=1))
    print(f"wrote {len(RESULTS)} predict samples for {len({r['id'] for r in RESULTS})} datasets")


def synth_fail(ds: str, name: str) -> None:
    """Called when a download is impossible: report, never invent rows silently."""
    print(f"  ! {ds} {name}: source unavailable; run again online (no synthetic rows written for real datasets)")


if __name__ == "__main__":
    main()
