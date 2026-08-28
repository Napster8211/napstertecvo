import httpx
from ..config import get_settings
class NIEBridge:
    def __init__(self): self.s=get_settings()
    async def send(self,event):
        if not self.s.nie_communication_webhook_url: return None
        h={"Content-Type":"application/json"}
        if self.s.nie_service_token: h["Authorization"]=f"Bearer {self.s.nie_service_token}"
        async with httpx.AsyncClient(timeout=self.s.http_timeout_seconds) as c:
            r=await c.post(self.s.nie_communication_webhook_url,json=event,headers=h)
        r.raise_for_status()
        try:return r.json()
        except:return {"status":"accepted"}
nie_bridge=NIEBridge()
