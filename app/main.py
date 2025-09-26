from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import httpx

from .settings import get_settings, Settings
from .db import get_supabase
from .schemas import (
    AgentConfigIn,
    AgentConfigOut,
    StartCallRequest,
    StartCallResponse,
    WebhookPayload,
    WebhookTestRequest,
)
from .retell import trigger_retell_call
from .summary import build_structured_summary
from .conversation_controller import (
    ConversationContext,
    build_system_prompt,
    generate_reply,
)
from .llm_client import GeminiClient, OpenAIClient, LLMClient


app = FastAPI(title="AI Voice Agent Backend", version="0.1.0")

# CORS - allow all by default; tighten in production via env
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/config", response_model=AgentConfigOut)
def upsert_config(
    payload: AgentConfigIn,
    settings: Settings = Depends(get_settings),
):
    supabase = get_supabase(settings)

    data = {
        "name": payload.name,
        "prompt": payload.prompt,
        "settings": payload.settings,
    }

    if payload.id is not None:
        # update existing
        result = (
            supabase.table("agent_config")
            .update(data)
            .eq("id", payload.id)
            .execute()
        )
        rows = result.data or []
        if not rows:
            raise HTTPException(status_code=404, detail="Config not found")
        row = rows[0]
    else:
        # insert new
        result = supabase.table("agent_config").insert(data).execute()
        rows = result.data or []
        row = rows[0]

    return AgentConfigOut(
        id=row.get("id"),
        name=row.get("name"),
        prompt=row.get("prompt"),
        settings=row.get("settings"),
        created_at=row.get("created_at"),
    )


@app.get("/configs")
def get_all_configs(settings: Settings = Depends(get_settings)):
    supabase = get_supabase(settings)
    try:
        result = supabase.table("agent_config").select("id,name").order("created_at", desc=True).execute()
        return result.data or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch configs: {str(e)}")


@app.get("/config/{config_id}", response_model=AgentConfigOut)
def get_config(config_id: int, settings: Settings = Depends(get_settings)):
    supabase = get_supabase(settings)
    result = supabase.table("agent_config").select("*").eq("id", config_id).limit(1).execute()
    rows = result.data or []
    if not rows:
        raise HTTPException(status_code=404, detail="Config not found")
    row = rows[0]
    return AgentConfigOut(
        id=row.get("id"),
        name=row.get("name"),
        prompt=row.get("prompt"),
        settings=row.get("settings"),
        created_at=row.get("created_at"),
    )


@app.post("/start-call", response_model=StartCallResponse)
def start_call(request_body: StartCallRequest, settings: Settings = Depends(get_settings)):
    supabase = get_supabase(settings)

    # Validate config exists
    cfg = (
        supabase.table("agent_config").select("id,prompt,settings").eq("id", request_body.config_id).limit(1).execute()
    )
    if not (cfg.data and len(cfg.data) == 1):
        raise HTTPException(status_code=400, detail="Invalid config_id")
    
    # Get agent_id from settings - required for real Retell AI calls
    config_data = cfg.data[0] or {}
    agent_id = config_data.get("settings", {}).get("retell_agent_id")
    if not agent_id:
        raise HTTPException(
            status_code=400, 
            detail="Agent configuration must include 'retell_agent_id' in settings. Please configure your Retell AI agent first."
        )

    # Trigger Retell
    try:
        retell_result = trigger_retell_call(
            api_key=settings.retell_api_key,
            driver_name=request_body.driver_name,
            phone_number=request_body.phone_number,
            load_number=request_body.load_number,
            agent_id=agent_id,
            config_id=request_body.config_id,
            base_url=f"{settings.retell_base_url.rstrip('/')}{settings.retell_start_call_path if settings.retell_start_call_path.startswith('/') else '/' + settings.retell_start_call_path}",
            webhook_url=f"{settings.webhook_base_url}/webhook",
            voice_settings=(config_data.get("settings", {}).get("voice_settings") if isinstance(config_data.get("settings"), dict) else None),
            from_number=settings.retell_from_number or None,
        )
    except Exception as exc:  # pragma: no cover - external API
        raise HTTPException(status_code=502, detail=f"Retell API error: {exc}")

    external_call_id: Optional[str] = retell_result.get("call_id") if isinstance(retell_result, dict) else None

    # Save initial call log
    insert_payload = {
        "driver_name": request_body.driver_name,
        "phone_number": request_body.phone_number,
        "load_number": request_body.load_number,
        "transcript": None,
        "structured_summary": None,
        "external_call_id": external_call_id,
        "config_id": request_body.config_id,
    }
    # Ensure columns exist in Supabase: external_call_id, config_id
    result = supabase.table("call_logs").insert(insert_payload).execute()
    row = (result.data or [None])[0]
    if row is None:
        raise HTTPException(status_code=500, detail="Failed to save call log")

    return StartCallResponse(call_id=row.get("id"), external_call_id=external_call_id)


@app.post("/webhook")
async def webhook(req: Request, settings: Settings = Depends(get_settings)):
    # Accepts Retell webhook JSON (event-based). For simplicity, handle text events and final transcript.
    payload_json = await req.json()
    try:
        payload = WebhookPayload(**payload_json)
    except Exception:
        # Accept lenient payloads from external service
        payload = WebhookPayload(
            call_id=payload_json.get("call_id"),
            transcript=payload_json.get("transcript", ""),
            metadata=payload_json.get("metadata", {}),
        )

    supabase = get_supabase(settings)

    # Determine which log row to update
    call_log_query = supabase.table("call_logs").select("id").eq("external_call_id", payload.call_id).limit(1)
    result = call_log_query.execute()
    rows = result.data or []
    if not rows and isinstance(payload.call_id, int):
        # fallback if webhook sends our internal id
        result = supabase.table("call_logs").select("id").eq("id", payload.call_id).limit(1).execute()
        rows = result.data or []
    if not rows:
        raise HTTPException(status_code=404, detail="Call log not found")
    call_log_id = rows[0]["id"]

    # Live conversation loop (simplified): when we receive an incremental transcript line, generate a reply.
    # This assumes Retell posts partial transcripts as events with metadata. Adjust to Retell's event schema if needed.
    event_type = payload_json.get("event") or payload_json.get("type")

    # Fetch config and conversation context if possible
    config_id = payload.metadata.get("config_id") if isinstance(payload.metadata, dict) else None
    driver_name = payload.metadata.get("driver_name") if isinstance(payload.metadata, dict) else None
    load_number = payload.metadata.get("load_number") if isinstance(payload.metadata, dict) else None

    if event_type in {"transcript.partial", "transcript.final", "asr.partial", "asr.final"} and payload.transcript:
        # Load agent prompt/settings
        system_prompt = ""
        behavior_settings = {}
        if config_id is not None:
            try:
                cfg = get_supabase(settings).table("agent_config").select("prompt,settings").eq("id", config_id).limit(1).execute()
                if cfg.data:
                    system_prompt = cfg.data[0].get("prompt") or ""
                    behavior_settings = cfg.data[0].get("settings") or {}
            except Exception:
                pass

        ctx = ConversationContext(
            system_prompt=build_system_prompt(system_prompt, ConversationContext(
                system_prompt="",
                settings=behavior_settings or {},
                call_id=str(payload.call_id) if payload.call_id is not None else None,
                load_number=load_number,
                driver_name=driver_name,
            )),
            settings=behavior_settings or {},
            call_id=str(payload.call_id) if payload.call_id is not None else None,
            load_number=load_number,
            driver_name=driver_name,
        )

        llm: LLMClient | None = None
        if settings.gemini_api_key:
            llm = GeminiClient(api_key=settings.gemini_api_key, model=settings.gemini_model)
        elif settings.openai_api_key:
            llm = OpenAIClient(api_key=settings.openai_api_key, model=settings.openai_model)

        if llm:
            reply_text = generate_reply(llm, ctx, payload.transcript)

            # Send reply back to Retell (placeholder endpoint - adjust per Retell API to send TTS/assistant message)
            try:
                with httpx.Client(timeout=10.0) as client:
                    client.post(
                        f"{settings.retell_base_url.rstrip('/')}{settings.retell_reply_path if settings.retell_reply_path.startswith('/') else '/' + settings.retell_reply_path}",
                        headers={
                            "Authorization": f"Bearer {settings.retell_api_key}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "call_id": payload.call_id,
                            "text": reply_text,
                        },
                    )
            except Exception:
                pass

    summary = build_structured_summary(payload.transcript)

    update_data = {
        "transcript": payload.transcript,
        "structured_summary": summary,
    }
    supabase.table("call_logs").update(update_data).eq("id", call_log_id).execute()

    return JSONResponse({"ok": True, "call_log_id": call_log_id})


@app.post("/webhook/test")
def webhook_test(payload: WebhookTestRequest):
    summary = build_structured_summary(payload.transcript)
    return {"ok": True, "structured_summary": summary}


@app.get("/call-logs")
def get_call_logs(settings: Settings = Depends(get_settings)):
    supabase = get_supabase(settings)
    
    try:
        result = supabase.table("call_logs").select("*").order("created_at", desc=True).execute()
        return {"messages": result.data or []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch call logs: {str(e)}")


@app.get("/webhook/examples")
def webhook_examples():
    examples = [
        {
            "description": "Scenario 1: Driver Check-in - Arrival Confirmation",
            "payload": {
                "call_id": "rt-12345",
                "transcript": "Hi Mike, this is Dispatch with a check call on load 7891-B. Can you give me an update on your status? I've arrived at the destination and I'm unloading now. Everything went smoothly.",
                "metadata": {"driver": "Mike", "load_number": "7891-B"},
            },
        },
        {
            "description": "Scenario 1: Driver Check-in - In-Transit Update",
            "payload": {
                "call_id": "rt-67890",
                "transcript": "Hi Sarah, this is Dispatch with a check call on load 7892-C. Can you give me an update on your status? I'm currently driving on I-10 near Indio, CA. I should arrive tomorrow at 8:00 AM. Everything is going well.",
                "metadata": {"driver": "Sarah", "load_number": "7892-C"},
            },
        },
        {
            "description": "Scenario 2: Emergency Protocol - Breakdown",
            "payload": {
                "call_id": "rt-54321",
                "transcript": "Hi Tom, this is Dispatch with a check call on load 7893-D. Can you give me an update on your status? Emergency! I just had a blowout, I'm pulling over to the side of I-15 North at mile marker 123. Need immediate assistance.",
                "metadata": {"driver": "Tom", "load_number": "7893-D"},
            },
        },
        {
            "description": "Special Case: Uncooperative Driver",
            "payload": {
                "call_id": "rt-11223",
                "transcript": "Hi, this is Dispatch with a check call on load 7894-E. Can you give me an update on your status? Yeah. Driving. Okay. Later.",
                "metadata": {"driver": "Uncooperative Driver", "load_number": "7894-E"},
            },
        },
        {
            "description": "Special Case: Noisy Environment",
            "payload": {
                "call_id": "rt-55667",
                "transcript": "Hi, this is Dispatch with a check call on load 7895-F. Can you give me an update on your status? [inaudible] driving [garbled] traffic [unclear] can't hear you [inaudible]",
                "metadata": {"driver": "Noisy Environment", "load_number": "7895-F"},
            },
        },
    ]
    return {"examples": examples}


__all__ = ["app"]


