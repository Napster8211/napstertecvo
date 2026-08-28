from fastapi import APIRouter,Request
from ..services.nie_bridge import nie_bridge
router=APIRouter(prefix="/webhooks")

@router.post("/arkesel/voice-status")
async def voice_status(request:Request):
    try:p=await request.json()
    except:p=dict(await request.form())
    event={"provider":"arkesel","provider_call_id":p.get("call_id") or p.get("id"),"direction":"outbound","status":str(p.get("status") or "unknown"),"metadata":p}
    await nie_bridge.send(event); return {"status":"accepted"}

@router.post("/arkesel/voiceconnect")
async def voiceconnect(request:Request):
    p=await request.json()
    event={"provider":"arkesel_voiceconnect","provider_call_id":p.get("call_id") or p.get("id"),"direction":p.get("direction","inbound"),"from_number":p.get("from") or p.get("from_number"),"to_number":p.get("to") or p.get("to_number"),"status":str(p.get("status") or p.get("event") or "unknown"),"transcript":p.get("transcript"),"metadata":p}
    result=await nie_bridge.send(event); return {"status":"accepted","nie":result}
