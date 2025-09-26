from typing import Dict, Any, Optional, List, Tuple
import httpx


def trigger_retell_call(
    api_key: str,
    driver_name: str,
    phone_number: str,
    load_number: str,
    agent_id: str,
    config_id: int,
    base_url: str = "https://api.retellai.com",
    webhook_url: str = None,
    voice_settings: Optional[Dict[str, Any]] = None,
    from_number: Optional[str] = None,
) -> Dict[str, Any]:
    if not api_key:
        raise ValueError("RETELL_API_KEY is not configured")
    
    if not agent_id:
        raise ValueError("Agent ID is required for Retell AI calls")

    # Build candidate endpoints to auto-discover correct start-call path
    base_host = base_url.split("/v2/")[0].rstrip("/")
    candidates: List[str] = []
    # If caller provided a full path, try it first
    if base_url.startswith("http") and "/v" in base_url:
        candidates.append(base_url)
        base_host = base_url.split("/v")[0].rstrip("/")
    # Common variants
    for path in [
        "/v2/create-phone-call",
        "/v2/phone-calls",
        "/v2/calls/start",
        "/v2/calls",
        "/v1/phone-calls",
        "/v1/calls",
    ]:
        candidates.append(f"{base_host}{path}")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    
    # Retell AI API payload structure
    payload: Dict[str, Any] = {
        "agent_id": agent_id,
        "to_number": phone_number,
        "metadata": {
            "driver_name": driver_name,
            "load_number": load_number,
            "config_id": config_id,
        },
        "webhook_url": webhook_url or f"{base_url.replace('api.retellai.com', 'your-domain.com')}/webhook",
    }

    # Include from_number only if provided and valid for your Retell account
    if from_number:
        payload["from_number"] = from_number

    # Forward supported runtime voice/behavior settings if Retell accepts overrides
    # Example fields (adjust based on Retell API docs):
    #   voice_id, speed, backchanneling, filler_words, interruption_sensitivity
    if voice_settings:
        allowed = {"voice_id", "speed", "backchanneling", "filler_words", "interruption_sensitivity"}
        overrides = {k: v for k, v in voice_settings.items() if k in allowed}
        if overrides:
            payload["voice_overrides"] = overrides

    errors: List[Tuple[str, str]] = []
    with httpx.Client(timeout=30.0) as client:
        for url in candidates:
            try:
                resp = client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                return resp.json()
            except httpx.HTTPStatusError as e:
                status = e.response.status_code
                try:
                    body = e.response.json()
                except Exception:
                    body = {"text": e.response.text}
                # For 400, we likely have the right endpoint but missing fields; bubble up immediately for clarity
                if status == 400:
                    detail = body.get("detail") or body.get("error_message") or body
                    raise ValueError(f"Retell AI API error: Bad request - {detail}")
                if status == 401:
                    raise ValueError("Invalid Retell AI API key")
                # Accumulate and continue trying alternatives for 404 etc.
                errors.append((url, f"{status} - {body}"))
            except httpx.ConnectError:
                errors.append((url, "connect-error"))
            except Exception as e:
                errors.append((url, f"unexpected-error: {e}"))

    # If we got here, none worked
    attempted = "; ".join([f"{u} => {err}" for u, err in errors[:4]])
    raise ValueError(f"Retell AI endpoint not found or unreachable. Tried: {attempted}")


__all__ = ["trigger_retell_call"]


