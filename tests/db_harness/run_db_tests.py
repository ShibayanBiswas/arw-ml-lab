"""Apply supabase/migrations/*.sql to a throw-away Postgres and run supabase/tests/*.sql.

Fallback when Docker / `supabase start` is unavailable (CI uses `supabase test db`).
Usage: pip install pgserver && python tests/db_harness/run_db_tests.py
Exit code 1 if a migration fails or any assertion prints "NOT OK".

Phase 0 note: on Windows, quote the pgserver `psql` path when the repo lives under a
directory with spaces (e.g. OneDrive Desktop).
"""

from __future__ import annotations

import glob
import os
import shutil
import subprocess
import sys
import tempfile

import pgserver  # bundles Postgres binaries (pip install pgserver)

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _data_dir() -> str:
    preferred = os.environ.get("LOCALAPPDATA") or tempfile.gettempdir()
    if " " in preferred and os.name == "nt":
        preferred = r"C:\Temp"
        os.makedirs(preferred, exist_ok=True)
    return tempfile.mkdtemp(prefix="labpg_", dir=preferred)


def _psql(srv: object, sql: str) -> str:
    uri = srv.get_uri()  # type: ignore[attr-defined]
    executable = os.path.join(
        os.path.dirname(pgserver.__file__),
        "pginstall",
        "bin",
        "psql.exe" if os.name == "nt" else "psql",
    )
    if not os.path.isfile(executable):
        return srv.psql(sql)  # type: ignore[attr-defined]
    # Quote executable only — matches pgserver's shell form but is space-safe.
    cmd = f'"{executable}" "{uri}"'
    result = subprocess.run(
        cmd,
        input=sql,
        text=True,
        capture_output=True,
        check=False,
        shell=True,
        encoding="utf-8",
        errors="replace",
    )
    return (result.stdout or "") + (result.stderr or "")


def _migration_failed(out: str) -> bool:
    cleaned = out.replace('ERROR:  extension "pgcrypto" is not available', "")
    # Ignore follow-on DETAIL/HINT for the missing optional extension.
    lines = [
        ln
        for ln in cleaned.splitlines()
        if "pgcrypto" not in ln.lower() and not ln.startswith("psql: warning:")
    ]
    return any(ln.startswith("ERROR:") for ln in lines)


data = _data_dir()
srv = pgserver.get_server(data, cleanup_mode="stop")
failed = False
with open(
    os.path.join(os.path.dirname(__file__), "supabase_stub.sql"), encoding="utf-8"
) as fh:
    _psql(srv, fh.read())
for f in sorted(glob.glob(os.path.join(ROOT, "supabase", "migrations", "*.sql"))):
    with open(f, encoding="utf-8") as fh:
        out = _psql(srv, fh.read())
    bad = _migration_failed(out)
    failed |= bad
    print(
        ("FAIL " if bad else "ok   ")
        + os.path.basename(f)
        + (("\n" + out[-600:]) if bad else "")
    )
for f in sorted(glob.glob(os.path.join(ROOT, "supabase", "tests", "*.sql"))):
    with open(f, encoding="utf-8") as fh:
        out = _psql(srv, fh.read())
    print("== " + os.path.basename(f))
    for line in out.splitlines():
        if "ok -" in line.lower() or line.startswith("ERROR:"):
            print(line)
            failed |= ("NOT OK" in line) or line.startswith("ERROR:")
shutil.rmtree(data, ignore_errors=True)
sys.exit(1 if failed else 0)
