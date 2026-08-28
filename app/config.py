from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    voice_gateway_api_key: str = "local-dev-change-me"

    piper_voice_name: str = "en_US-lessac-medium"
    piper_voice_path: str = (
        "/root/.local/share/piper/voices/en_US-lessac-medium.onnx"
    )
    piper_sample_rate: int = 22050

    arkesel_api_key: str = ""
    arkesel_voice_sms_url: str = (
        "https://sms.arkesel.com/api/v2/sms/voice/send"
    )
    arkesel_voice_id: str = "en-GH-female"
    arkesel_sender_id: str = "NapsterTec"

    arkesel_voiceconnect_enabled: bool = False
    arkesel_voiceconnect_base_url: str = ""
    arkesel_voiceconnect_token: str = ""

    nie_communication_webhook_url: str = ""
    nie_service_token: str = ""

    http_timeout_seconds: float = 15.0
    max_tts_chars: int = 2000

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
