"""
LLM Inspection Proxy — Logs everything, forwards to Ollama with proper streaming.
No API key needed.

Usage:
  1. pip install fastapi uvicorn rich httpx
  2. ollama serve
  3. python llm_proxy.py
  4. interpreter --model openai/gpt-4o --api-key dummy --api-base http://localhost:8080/v1
"""

import json
import uvicorn
import traceback
import httpx

from datetime import datetime, timezone
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint

app = FastAPI()
console = Console()

LOG_FILE     = Path(__file__).parent / "intercepted.jsonl"
OLLAMA_URL   = "http://localhost:11434/v1/chat/completions"
OLLAMA_MODEL = "llama3.2"


def log_to_file(data: dict):
    try:
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(data) + "\n")
    except Exception as e:
        console.print(f"[red]Log write error: {e}[/red]")


def print_messages(messages: list):
    color_map = {
        "system":    "red",
        "user":      "green",
        "assistant": "blue",
        "tool":      "yellow",
    }
    for msg in messages:
        role    = msg.get("role", "unknown")
        content = msg.get("content", "")
        if isinstance(content, list):
            content = json.dumps(content, indent=2)
        color = color_map.get(role, "white")
        console.print(Panel(
            Text(str(content)),
            title=f"[bold {color}]role: {role}[/bold {color}]",
            border_style=color,
            expand=False,
        ))


# ── /v1/models ─────────────────────────────────────────────────────────────────
@app.get("/v1/models")
async def list_models():
    console.print("[dim]→ /v1/models called[/dim]")
    return JSONResponse({
        "object": "list",
        "data": [{"id": "gpt-4o", "object": "model", "owned_by": "proxy"}]
    })


# ── /v1/chat/completions ───────────────────────────────────────────────────────
@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}

    messages  = body.get("messages", [])
    model     = body.get("model", "unknown")
    tools     = body.get("tools", [])
    stream    = body.get("stream", False)
    timestamp = datetime.now().strftime("%H:%M:%S")

    # ── Log to terminal ────────────────────────────────────────────────────────
    console.rule(f"[bold yellow]🔍 Intercepted @ {timestamp}[/bold yellow]")
    rprint(f"  [cyan]Model requested:[/cyan] {model}")
    rprint(f"  [cyan]Forwarding to:[/cyan]   Ollama ({OLLAMA_MODEL})")
    rprint(f"  [cyan]Stream:[/cyan]          {stream}")
    rprint(f"  [cyan]Messages:[/cyan]        {len(messages)}")
    rprint(f"  [cyan]Tools:[/cyan]           {len(tools)}")

    if tools:
        rprint("\n  [bold yellow]🛠  Tools passed:[/bold yellow]")
        for t in tools:
            fn   = t.get("function", t)
            name = fn.get("name", "?")
            desc = fn.get("description", "")[:100]
            rprint(f"    • [magenta]{name}[/magenta]: {desc}")

    if messages:
        console.print("\n[bold white]📨 Messages sent to model:[/bold white]")
        print_messages(messages)

    # ── Save to file ───────────────────────────────────────────────────────────
    log_to_file({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model":     model,
        "stream":    stream,
        "tools":     tools,
        "messages":  messages,
    })

    # Strip tools — local models don't support them
    ollama_body = {
        "model":    OLLAMA_MODEL,
        "messages": messages,
        "stream":   stream,
    }

    try:
        if stream:
            # ── True streaming — pass chunks through immediately as they arrive ──
            async def stream_generator():
                accumulated = []
                async with httpx.AsyncClient(timeout=120) as client:
                    async with client.stream("POST", OLLAMA_URL, json=ollama_body) as resp:
                        async for raw_bytes in resp.aiter_raw():
                            # Pass bytes through to Open Interpreter immediately
                            yield raw_bytes

                            # Also try to decode for logging
                            try:
                                text = raw_bytes.decode("utf-8")
                                for line in text.splitlines():
                                    if line.startswith("data:") and line.strip() != "data: [DONE]":
                                        chunk = json.loads(line[5:].strip())
                                        delta = chunk["choices"][0]["delta"]
                                        if delta.get("content"):
                                            accumulated.append(delta["content"])
                            except Exception:
                                pass

                # Print full response after stream ends
                full = "".join(accumulated)
                if full:
                    console.print("\n[bold white]📩 Ollama response:[/bold white]")
                    console.print(Panel(
                        Text(full),
                        title="[bold blue]role: assistant[/bold blue]",
                        border_style="blue",
                        expand=False
                    ))

            return StreamingResponse(
                stream_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "X-Accel-Buffering": "no",   # disable nginx buffering if any
                }
            )

        else:
            # ── Non-streaming ──────────────────────────────────────────────────
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(OLLAMA_URL, json=ollama_body)
                data = resp.json()

            reply = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            if reply:
                console.print("\n[bold white]📩 Ollama response:[/bold white]")
                console.print(Panel(
                    Text(reply),
                    title="[bold blue]role: assistant[/bold blue]",
                    border_style="blue",
                    expand=False
                ))

            return JSONResponse(data)

    except httpx.ConnectError:
        console.print("[bold red]❌ Could not connect to Ollama![/bold red]")
        console.print("   Make sure Ollama is running: [cyan]ollama serve[/cyan]")
        return JSONResponse({"error": "Ollama not running"}, status_code=503)

    except Exception as e:
        console.print(f"[bold red]❌ Error:[/bold red] {e}")
        console.print(traceback.format_exc())
        return JSONResponse({"error": str(e)}, status_code=500)


# ── Catch-all ──────────────────────────────────────────────────────────────────
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"])
async def catchall(request: Request, path: str):
    console.print(f"[dim]→ Other endpoint: /{path}[/dim]")
    return JSONResponse({})


# ── Global error handler ───────────────────────────────────────────────────────
@app.middleware("http")
async def catch_exceptions(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        console.print(f"[bold red]💥 Error:[/bold red] {e}")
        console.print(traceback.format_exc())
        return JSONResponse({"error": str(e)}, status_code=500)


if __name__ == "__main__":
    console.print(Panel(
        "[bold green]LLM Inspection Proxy → Ollama (streaming)[/bold green]\n\n"
        f"Forwarding to: [cyan]Ollama ({OLLAMA_MODEL})[/cyan]\n\n"
        "Run Open Interpreter:\n"
        "  [cyan]interpreter --model openai/gpt-4o --api-key dummy --api-base http://localhost:8080/v1[/cyan]\n\n"
        f"Logs saved to: [cyan]{LOG_FILE}[/cyan]",
        title="🔍 Proxy → Ollama",
        border_style="green",
    ))
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="warning")
