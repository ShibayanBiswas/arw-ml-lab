# ARW ML Lab — local developer commands (Phase 0+)
# On Windows without GNU make, use the PowerShell equivalents in docs/PHASE_0_REPORT.md
# or: `uv run` / `pnpm` / `supabase` / `docker compose` directly.

.PHONY: dev test lint db-reset db-test compose-up compose-down

dev:
	supabase start
	docker compose -f infra/docker-compose.yml up --build

compose-up:
	docker compose -f infra/docker-compose.yml up --build

compose-down:
	docker compose -f infra/docker-compose.yml down

test:
	uv run pytest tests/unit tests/contract_tradinglab tests/golden -q
	cd frontend && pnpm test --run
	@echo "DB tests: run 'make db-test' (Docker) or 'uv run python tests/db_harness/run_db_tests.py'"

lint:
	uv run ruff check labcore backend tests
	uv run ruff format --check labcore backend tests
	uv run mypy labcore
	cd frontend && pnpm lint && pnpm exec tsc --noEmit

db-reset:
	supabase db reset

db-test:
	supabase test db
