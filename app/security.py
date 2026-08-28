import hmac
from fastapi import Header, HTTPException
from .config import get_settings

async def require_internal_key(x_napstertec_key: str|None=Header(None, alias="X-NapsterTec-Key")):
    expected=get_settings().voice_gateway_api_key
    if not expected or not x_napstertec_key: raise HTTPException(401,"UNAUTHORIZED")
    if not hmac.compare_digest(str(expected),str(x_napstertec_key)): raise HTTPException(403,"FORBIDDEN")
