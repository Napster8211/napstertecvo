from fastapi import APIRouter,Depends,HTTPException
from ..security import require_internal_key
from ..schemas import VoiceMessageRequest,OutboundLeadCallRequest
from ..providers.arkesel_voice_sms import arkesel_voice_sms
from ..services.dnc import dnc
router=APIRouter(prefix="/api/v1",dependencies=[Depends(require_internal_key)])

@router.post("/calls/voice-message")
async def voice_message(req:VoiceMessageRequest):
    if dnc.contains(req.recipient): raise HTTPException(409,"RECIPIENT_ON_DNC_LIST")
    return await arkesel_voice_sms.send(req.recipient,req.message,req.voice_id,req.sender_id)

@router.post("/calls/outbound-lead")
async def outbound_lead(req:OutboundLeadCallRequest):
    if not req.approved or not req.approval_reference.strip(): raise HTTPException(403,"OUTBOUND_CALL_APPROVAL_REQUIRED")
    if dnc.contains(req.recipient): raise HTTPException(409,"RECIPIENT_ON_DNC_LIST")
    return await arkesel_voice_sms.send(req.recipient,req.message)

@router.post("/dnc/{phone}")
async def add_dnc(phone:str): dnc.add(phone); return {"status":"ok"}
@router.delete("/dnc/{phone}")
async def remove_dnc(phone:str): dnc.remove(phone); return {"status":"ok"}
