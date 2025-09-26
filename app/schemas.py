from typing import Optional, Any, Dict
from pydantic import BaseModel, Field


class AgentConfigIn(BaseModel):
    id: Optional[int] = Field(default=None)
    name: str
    prompt: str
    settings: Dict[str, Any] = Field(default_factory=dict)


class AgentConfigOut(BaseModel):
    id: int
    name: str
    prompt: str
    settings: Dict[str, Any]
    created_at: Optional[str] = None


class StartCallRequest(BaseModel):
    driver_name: str
    phone_number: str
    load_number: str
    config_id: int


class StartCallResponse(BaseModel):
    call_id: int
    external_call_id: Optional[str] = None


class WebhookPayload(BaseModel):
    call_id: Optional[str | int] = None
    transcript: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WebhookTestRequest(BaseModel):
    transcript: str


