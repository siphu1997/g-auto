# TLBB Automation Framework

Windows-first automation framework for TLBB on `LDPlayer 9`, built around a Python worker, a local FastAPI dashboard, ADB device control, and template-first UI recognition.

## MVP Scope
- Emulator: `LDPlayer 9`
- Platform: `Windows`
- Mode: `1 account / 1 instance`
- Recognition: template matching with OCR fallback
- Runtime: background worker + local dashboard
- Implemented task scope: `launch`, `claim_reward`, `claim_mail`

## Architecture
- `apps/api`: FastAPI entrypoint for JSON endpoints and local HTML dashboard
- `apps/worker`: CLI entrypoint for starting the background worker
- `src/core`: config, logging, device, vision, state machine, recovery, runtime
- `src/games/tlbb`: TLBB-specific screen signatures, task rules, and template profile metadata
- `src/dashboard/templates`: server-rendered dashboard pages
- `config`: YAML config files
- `tests`: unit and integration coverage with mocked device and vision fixtures

## Quick Start
```bash
uv venv
uv pip install -e ".[dev]"
uv run uvicorn apps.api.main:app --reload
```

Worker CLI:
```bash
uv run python -m apps.worker.main
```

## Dashboard and API
- Home: `/`
- Logs: `/logs/view`
- Screenshots: `/screenshots/view`
- Tasks: `/tasks/view`
- Config: `/config/view`

Core API:
- `GET /health`
- `GET /status`
- `GET /logs`
- `GET /screenshots/latest`
- `POST /bot/start`
- `POST /bot/stop`
- `POST /bot/restart`
- `POST /tasks/run`
- `POST /config/reload`

## Config Files
- `config/app.yaml`
- `config/emulator.yaml`
- `config/bot.yaml`
- `config/tasks.yaml`
- `config/vision.yaml`
- `config/recovery.yaml`
- `config/schedules.yaml`

`config/vision.yaml` ships with placeholder template metadata only. Real gameplay usage still requires capturing and storing actual template assets under `src/games/tlbb/templates/<profile>/`.

## Documentation
- [docs/00-overview.md](docs/00-overview.md)
- [docs/01-product-requirements.md](docs/01-product-requirements.md)
- [docs/02-architecture.md](docs/02-architecture.md)
- [docs/03-state-machine.md](docs/03-state-machine.md)
- [docs/04-vision-system.md](docs/04-vision-system.md)
- [docs/05-device-control.md](docs/05-device-control.md)
- [docs/06-task-flows.md](docs/06-task-flows.md)
- [docs/07-config-schema.md](docs/07-config-schema.md)
- [docs/08-logging-and-debugging.md](docs/08-logging-and-debugging.md)
- [docs/09-dashboard.md](docs/09-dashboard.md)
- [docs/10-testing-strategy.md](docs/10-testing-strategy.md)
- [docs/11-deployment-and-ops.md](docs/11-deployment-and-ops.md)
- [docs/12-roadmap.md](docs/12-roadmap.md)
- [docs/implementation-plan.md](docs/implementation-plan.md)
