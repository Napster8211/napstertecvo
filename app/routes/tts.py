import io
import wave

from fastapi import APIRouter, Depends
from fastapi.responses import Response, StreamingResponse

from ..config import get_settings
from ..security import require_internal_key
from ..schemas import TTSRequest
from ..providers.piper_tts import piper_tts

router = APIRouter(
    prefix="/api/v1/tts",
    dependencies=[Depends(require_internal_key)],
)

@router.post("/stream")
async def stream(req: TTSRequest):
    async def gen():
        async for audio_chunk in piper_tts.stream_pcm(req.text):
            yield audio_chunk

    settings = get_settings()
    return StreamingResponse(
        gen(),
        media_type="application/octet-stream",
        headers={
            "X-Audio-Format": "pcm_s16le",
            "X-Sample-Rate": str(settings.piper_sample_rate),
            "X-Channels": "1",
        },
    )

@router.post("/wav")
async def wav(req: TTSRequest):
    settings = get_settings()
    pcm = bytearray()
    async for audio_chunk in piper_tts.stream_pcm(req.text):
        pcm.extend(audio_chunk)

    output = io.BytesIO()
    with wave.open(output, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(settings.piper_sample_rate)
        wav_file.writeframes(bytes(pcm))

    return Response(
        output.getvalue(),
        media_type="audio/wav",
        headers={
            "X-Audio-Format": "wav",
            "X-Sample-Rate": str(settings.piper_sample_rate),
            "X-Channels": "1",
        },
    )
