from enum import Enum
from typing import Any
from pydantic import BaseModel, Field

class CallDirection(str,Enum):
    INBOUND="inbound"; OUTBOUND="outbound"

class TTSRequest(BaseModel):
    text:str=Field(min_length=1,max_length=5000)

class VoiceMessageRequest(BaseModel):
    recipient:str
    message:str=Field(min_length=1,max_length=5000)
    voice_id:str|None=None
    sender_id:str|None=None

class OutboundLeadCallRequest(BaseModel):
    lead_id:str
    recipient:str
    purpose:str
    message:str=Field(min_length=1,max_length=5000)
    approved:bool=False
    approval_reference:str=""

class CallEvent(BaseModel):
    provider:str
    provider_call_id:str|None=None
    direction:CallDirection
    from_number:str|None=None
    to_number:str|None=None
    status:str
    transcript:str|None=None
    metadata:dict[str,Any]=Field(default_factory=dict)
