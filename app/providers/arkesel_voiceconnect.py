"""Safe integration boundary. Do not invent undocumented Arkesel endpoints."""
from ..config import get_settings

class ArkeselVoiceConnectProvider:
    def __init__(self): self.s=get_settings()
    @property
    def configured(self):
        return bool(self.s.arkesel_voiceconnect_enabled and self.s.arkesel_voiceconnect_base_url and self.s.arkesel_voiceconnect_token)
    async def start_live_outbound_call(self,*a,**k):
        if not self.configured: raise RuntimeError("ARKESEL_VOICECONNECT_NOT_CONFIGURED")
        raise NotImplementedError("Implement only from NapsterTec's official VoiceConnect API/SIP contract.")
    async def accept_live_inbound_call(self,*a,**k):
        if not self.configured: raise RuntimeError("ARKESEL_VOICECONNECT_NOT_CONFIGURED")
        raise NotImplementedError("Implement only from NapsterTec's official VoiceConnect API/SIP contract.")

arkesel_voiceconnect=ArkeselVoiceConnectProvider()
