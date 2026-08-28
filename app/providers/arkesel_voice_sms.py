import httpx
from ..config import get_settings

class ArkeselVoiceSmsProvider:
    def __init__(self): self.s=get_settings()
    async def send(self,recipient,message,voice_id=None,sender_id=None):
        if not self.s.arkesel_api_key: raise RuntimeError("ARKESEL_API_KEY_NOT_CONFIGURED")
        payload={"recipient":recipient,"message":message,"voice_id":voice_id or self.s.arkesel_voice_id,"sender_id":sender_id or self.s.arkesel_sender_id}
        headers={"api-key":self.s.arkesel_api_key,"Content-Type":"application/json"}
        async with httpx.AsyncClient(timeout=self.s.http_timeout_seconds) as c:
            r=await c.post(self.s.arkesel_voice_sms_url,json=payload,headers=headers)
        r.raise_for_status(); return r.json()

arkesel_voice_sms=ArkeselVoiceSmsProvider()
