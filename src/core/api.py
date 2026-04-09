from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import parse_qs

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from core.bot_runtime import BotRuntime


def create_app(runtime: BotRuntime | None = None) -> FastAPI:
    app = FastAPI(title="TLBB Automation API")
    app.state.runtime = runtime or BotRuntime()

    template_dir = Path(__file__).resolve().parents[1] / "dashboard" / "templates"
    templates = Jinja2Templates(directory=str(template_dir))

    def get_runtime() -> BotRuntime:
        return app.state.runtime

    def ui_or_api_response(request: Request, payload: object, redirect_target: str) -> JSONResponse | RedirectResponse:
        if request.headers.get("referer"):
            return RedirectResponse(url=redirect_target, status_code=303)
        return JSONResponse(payload)

    async def extract_task_name(request: Request) -> str | None:
        content_type = request.headers.get("content-type", "")
        raw = await request.body()
        if "application/json" in content_type:
            try:
                payload = json.loads(raw.decode() or "{}")
            except json.JSONDecodeError:
                return None
            return payload.get("task")
        parsed = parse_qs(raw.decode())
        values = parsed.get("task", [])
        return values[0] if values else None

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/status")
    async def status() -> object:
        return get_runtime().get_status()

    @app.get("/logs")
    async def logs(
        limit: int = Query(default=100, ge=1, le=500),
        module: str | None = None,
        level: str | None = None,
    ) -> list[dict[str, object]]:
        return get_runtime().latest_logs(limit=limit, module=module, level=level)

    @app.get("/screenshots/latest")
    async def latest_screenshot() -> FileResponse:
        runtime_instance = get_runtime()
        status_payload = runtime_instance.get_status()
        if not status_payload.latest_screenshot:
            raise HTTPException(status_code=404, detail="No screenshot captured yet")
        path = Path(status_payload.latest_screenshot)
        if not path.exists():
            raise HTTPException(status_code=404, detail="Latest screenshot path is missing")
        return FileResponse(path)

    @app.post("/bot/start", response_model=None)
    async def start_bot(request: Request):
        payload = get_runtime().start().model_dump(mode="json")
        return ui_or_api_response(request, payload, "/")

    @app.post("/bot/stop", response_model=None)
    async def stop_bot(request: Request):
        payload = get_runtime().stop().model_dump(mode="json")
        return ui_or_api_response(request, payload, "/")

    @app.post("/bot/restart", response_model=None)
    async def restart_bot(request: Request):
        payload = get_runtime().restart().model_dump(mode="json")
        return ui_or_api_response(request, payload, "/")

    @app.post("/tasks/run", response_model=None)
    async def run_task(request: Request):
        runtime_instance = get_runtime()
        task_name = await extract_task_name(request)
        if not task_name:
            raise HTTPException(status_code=400, detail="Missing task name")
        runtime_instance.enqueue_task(task_name)
        payload = runtime_instance.get_status().model_dump(mode="json")
        return ui_or_api_response(request, payload, "/tasks/view")

    @app.post("/config/reload", response_model=None)
    async def reload_config(request: Request):
        settings = get_runtime().reload_config()
        payload = settings.model_dump(mode="json")
        return ui_or_api_response(request, payload, "/config/view")

    @app.get("/")
    async def home_page(request: Request) -> object:
        return templates.TemplateResponse(
            request=request,
            name="home.html",
            context={"title": "Home", "status": get_runtime().get_status().model_dump(mode="json")},
        )

    @app.get("/logs/view")
    async def logs_page(request: Request) -> object:
        return templates.TemplateResponse(
            request=request,
            name="logs.html",
            context={"title": "Logs", "logs": get_runtime().latest_logs(limit=200)},
        )

    @app.get("/screenshots/view")
    async def screenshots_page(request: Request) -> object:
        latest = get_runtime().get_status().latest_screenshot
        return templates.TemplateResponse(
            request=request,
            name="screenshots.html",
            context={"title": "Screenshots", "latest": latest},
        )

    @app.get("/tasks/view")
    async def tasks_page(request: Request) -> object:
        return templates.TemplateResponse(
            request=request,
            name="tasks.html",
            context={"title": "Tasks", "tasks": get_runtime().available_tasks()},
        )

    @app.get("/config/view")
    async def config_page(request: Request) -> object:
        return templates.TemplateResponse(
            request=request,
            name="config.html",
            context={
                "title": "Config",
                "config": json.dumps(get_runtime().settings.model_dump(mode="json"), indent=2),
            },
        )

    return app
