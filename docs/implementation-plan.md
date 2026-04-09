# Save Plan Then Implement MVP

## Summary
- Save this plan as `docs/implementation-plan.md` in the next implementation turn.
- Then implement a Windows-first, single-instance MVP for `LDPlayer 9` with:
  - Python bot core
  - FastAPI local API
  - server-rendered local dashboard
  - ADB device control
  - template-first vision with OCR fallback
  - deterministic state machine and recovery
- Initial runnable feature scope is limited to:
  - `launch`
  - `claim_reward`
  - `claim_mail`
- Keep `daily`, `quest`, and `train` declared in config and task registry, but not implemented in the first coding pass.

## Implementation Changes
- Create repo skeleton matching the existing docs:
  - `apps/api`
  - `apps/worker`
  - `src/core`
  - `src/games/tlbb`
  - `config`
  - `data`
  - `tests`
- Add project bootstrap files:
  - `pyproject.toml`
  - `.python-version`
  - base `README.md` update only if implementation setup diverges from current docs
- Build core modules in this order:
  1. config loader and schema validation
  2. structured logger and artifact paths
  3. device controller over ADB
  4. vision registry, matcher, classifier, OCR adapter
  5. state machine and recovery ladder
  6. task engine with `launch`, `claim_reward`, `claim_mail`
  7. worker runtime loop
  8. FastAPI endpoints
  9. server-rendered dashboard pages
- Keep TLBB-specific logic inside `src/games/tlbb`:
  - screen definitions
  - templates
  - flow rules
  - profile mappings
- Use filesystem artifacts only for MVP:
  - logs
  - screenshots
  - overlay/debug outputs
- Do not add database storage, multi-instance support, or React frontend in this slice.

## Public Interfaces
- Implement config files:
  - `config/app.yaml`
  - `config/emulator.yaml`
  - `config/bot.yaml`
  - `config/tasks.yaml`
  - `config/vision.yaml`
  - `config/recovery.yaml`
  - `config/schedules.yaml`
- Implement internal contracts:
  - `DeviceController`
  - `VisionService`
  - `StateSnapshot`
  - `TaskContext`
  - `TaskResult`
  - `BotStatus`
- Implement HTTP endpoints:
  - `GET /health`
  - `GET /status`
  - `GET /logs`
  - `GET /screenshots/latest`
  - `POST /bot/start`
  - `POST /bot/stop`
  - `POST /bot/restart`
  - `POST /tasks/run`
  - `POST /config/reload`
- Implement dashboard pages:
  - Home
  - Logs
  - Screenshots
  - Tasks
  - Config

## Delivery Sequence
- Step 1: write `docs/implementation-plan.md` with this approved plan content.
- Step 2: scaffold the repo and dependency management.
- Step 3: implement config, logging, and device layer until screenshot and tap flows are testable.
- Step 4: implement vision MVP with profile-based templates and screen classification fixtures.
- Step 5: implement state machine, watchdog, and recovery.
- Step 6: implement `launch`, `claim_reward`, and `claim_mail`.
- Step 7: implement API and local HTML dashboard.
- Step 8: run unit, integration, and Windows smoke tests; fix gaps before expanding scope.

## Test Plan
- Unit tests:
  - config parsing
  - schema validation
  - timeout and retry policies
  - confidence threshold handling
  - transition guards
  - OCR normalization
- Integration tests:
  - mocked ADB client
  - screenshot pipeline
  - template matching on fixtures
  - screen classification on golden images
  - launch flow
  - reward flow
  - mail flow
  - unknown-state escalation
  - disconnect and restart recovery
- Manual Windows smoke tests on real `LDPlayer 9`:
  - connect emulator
  - launch game to `HOME_SCREEN`
  - run reward flow
  - run mail flow
  - validate dashboard controls
  - validate screenshot and log artifacts on forced failures

## Assumptions and Defaults
- Dashboard choice is `FastAPI + server-rendered HTML`, because this is a local operator console for Windows and emulator control.
- Runtime choice is `Windows-first`, with abstractions kept clean but no requirement that emulator control works cross-platform in MVP.
- OCR remains fallback-only and limited to cropped fixed regions.
- Persistence remains filesystem-only for MVP.
- First coding milestone is a runnable end-to-end MVP, not just framework scaffolding.

