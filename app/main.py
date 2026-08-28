from pathlib import Path

from fastapi import FastAPI, HTTPException

from .config import get_settings
from .routes.tts import router as tts
from .routes.calls import router as calls
from .routes.webhooks import router as webhooks


app = FastAPI(title="NapsterTec Voice Gateway", version="0.1.0")

app.include_router(tts)
app.include_router(calls)
app.include_router(webhooks)


@app.get("/health")
async def health():
    """Lightweight liveness endpoint for Render health checks."""
    s = get_settings()
    return {
        "status": "ok",
        "service": "napstertec-voice-gateway",
        "piper_voice": s.piper_voice_name,
        "arkesel_voice_sms_configured": bool(s.arkesel_api_key),
        "arkesel_voiceconnect_enabled": s.arkesel_voiceconnect_enabled,
    }


@app.get("/ready")
async def ready():
    """Readiness endpoint that verifies the configured Piper model files exist."""
    s = get_settings()

    model_path = Path(s.piper_voice_path)
    config_path = Path(f"{s.piper_voice_path}.json")

    checks = {
        "piper_model": model_path.is_file(),
        "piper_config": config_path.is_file(),
    }

    if not all(checks.values()):
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "service": "napstertec-voice-gateway",
                "checks": checks,
            },
        )

    return {
        "status": "ready",
        "service": "napstertec-voice-gateway",
        "piper_voice": s.piper_voice_name,
        "piper_sample_rate": s.piper_sample_rate,
        "checks": checks,
    }
