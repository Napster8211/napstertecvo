import io,wave
from fastapi import APIRouter,Depends
from fastapi.responses import Response,StreamingResponse
from ..security import require_internal_key
from ..schemas import TTSRequest
from ..providers.piper_tts import piper_tts
from ..config import get_settings
router=APIRouter(prefix="/api/v1/tts",dependencies=[Depends(require_internal_key)])

@router.post("/stream")
async def stream(req:TTSRequest):
    async def gen():
        async for b in piper_tts.stream_pcm(req.text): yield b
    s=get_settings()
    return StreamingResponse(gen(),media_type="application/octet-stream",headers={"X-Audio-Format":"pcm_s16le","X-Sample-Rate":str(s.piper_sample_rate),"X-Channels":"1"})

@router.post("/wav")
async def wav(req:TTSRequest):
    s=get_settings(); pcm=bytearray()
    async for b in piper_tts.stream_pcm(req.text): pcm.extend(b)
    out=io.BytesIO()
    with wave.open(out,"wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(s.piper_sample_rate); w.writeframes(bytes(pcm))
    return Response(out.getvalue(),media_type="audio/wav")
