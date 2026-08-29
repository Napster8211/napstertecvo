import os
import asyncio
import sys
import types
from unittest.mock import AsyncMock, patch

import pytest

try:
    from piper.voice import PiperVoice as _PiperVoice  # noqa: F401
except ModuleNotFoundError:
    piper_package = types.ModuleType("piper")
    piper_voice_module = types.ModuleType("piper.voice")

    class _TestPiperVoice:
        @classmethod
        def load(cls, _path):
            return cls()

    piper_voice_module.PiperVoice = _TestPiperVoice
    piper_package.voice = piper_voice_module
    sys.modules["piper"] = piper_package
    sys.modules["piper.voice"] = piper_voice_module

os.environ["VOICE_GATEWAY_API_KEY"]="test-secret"
from app.config import get_settings
get_settings.cache_clear()
from fastapi.testclient import TestClient
from app.main import app
from app.providers.piper_tts import PiperTTSProvider, piper_tts

c=TestClient(app)
def test_health(): assert c.get("/health").status_code==200
def test_auth(): assert c.post("/api/v1/dnc/+233200000000").status_code in (401,403)
def test_approval():
    r=c.post("/api/v1/calls/outbound-lead",headers={"X-NapsterTec-Key":"test-secret"},json={"lead_id":"l1","recipient":"+233200000000","purpose":"intro","message":"hello","approved":False,"approval_reference":""})
    assert r.status_code==403


def test_piper_preload_sets_loaded_state():
    provider = PiperTTSProvider()
    fake_voice = object()
    with patch("app.providers.piper_tts.PiperVoice.load", return_value=fake_voice):
        asyncio.run(provider.preload())
    assert provider.is_loaded is True


def test_ready_requires_loaded_piper():
    original_voice = piper_tts._voice
    try:
        piper_tts._voice = object()
        response = c.get("/ready")
        assert response.status_code == 200
        assert response.json()["checks"]["piper_loaded"] is True
    finally:
        piper_tts._voice = original_voice


def test_wav_response_exposes_playback_metadata():
    async def fake_pcm(_text):
        yield b"\x00\x00\x01\x00"

    with patch.object(piper_tts, "stream_pcm", new=fake_pcm):
        response = c.post(
            "/api/v1/tts/wav",
            headers={"X-NapsterTec-Key": "test-secret"},
            json={"text": "Gateway metadata test"},
        )

    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/wav"
    assert response.headers["X-Audio-Format"] == "wav"
    assert response.headers["X-Sample-Rate"]
    assert response.headers["X-Channels"] == "1"
    assert response.content.startswith(b"RIFF")


def test_lifespan_fails_closed_when_preload_fails():
    with patch.object(
        piper_tts,
        "preload",
        new=AsyncMock(side_effect=RuntimeError("PIPER_LOAD_FAILED")),
    ):
        with pytest.raises(RuntimeError, match="PIPER_LOAD_FAILED"):
            with TestClient(app):
                pass
