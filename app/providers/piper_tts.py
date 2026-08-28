import asyncio
from pathlib import Path
from typing import AsyncIterator, Final

from app.config import get_settings
from piper.voice import PiperVoice


class PiperTTSProvider:
    """Piper 1.7+ text-to-speech provider."""

    def __init__(self) -> None:
        self._voice: PiperVoice | None = None
        self._load_lock = asyncio.Lock()

    async def _get_voice(self) -> PiperVoice:
        if self._voice is not None:
            return self._voice

        async with self._load_lock:
            if self._voice is not None:
                return self._voice

            settings = get_settings()
            model_path = Path(settings.piper_voice_path).expanduser()

            if not model_path.is_file():
                raise RuntimeError(
                    f"PIPER_MODEL_NOT_FOUND: {model_path}"
                )

            self._voice = await asyncio.to_thread(
                PiperVoice.load,
                str(model_path),
            )
            return self._voice

    async def stream_pcm(self, text: str) -> AsyncIterator[bytes]:
        """
        Stream signed 16-bit little-endian PCM produced by Piper 1.7+.

        Piper synthesis is CPU-bound, so it runs in a worker thread.
        Generated AudioChunk objects are forwarded to the asyncio
        consumer as soon as they are available.
        """
        normalized_text = text.strip()
        if not normalized_text:
            return

        settings = get_settings()
        if len(normalized_text) > settings.max_tts_chars:
            raise ValueError(
                f"TTS_TEXT_TOO_LONG: maximum is "
                f"{settings.max_tts_chars} characters"
            )

        voice = await self._get_voice()
        loop = asyncio.get_running_loop()

        queue: asyncio.Queue[bytes | BaseException | object] = asyncio.Queue(
            maxsize=16
        )
        done: Final[object] = object()

        def put_from_worker(item: bytes | BaseException | object) -> None:
            future = asyncio.run_coroutine_threadsafe(
                queue.put(item),
                loop,
            )
            future.result()

        def worker() -> None:
            try:
                for chunk in voice.synthesize(normalized_text):
                    audio = getattr(
                        chunk,
                        "audio_int16_bytes",
                        None,
                    )

                    if audio is None:
                        audio = getattr(
                            chunk,
                            "audio_bytes",
                            None,
                        )

                    if audio is None and isinstance(chunk, bytes):
                        audio = chunk

                    if audio:
                        put_from_worker(bytes(audio))

            except BaseException as exc:
                put_from_worker(exc)

            finally:
                put_from_worker(done)

        worker_task = asyncio.create_task(
            asyncio.to_thread(worker)
        )

        try:
            while True:
                item = await queue.get()

                if item is done:
                    break

                if isinstance(item, BaseException):
                    raise item

                if not isinstance(item, bytes):
                    raise RuntimeError(
                        "PIPER_INVALID_AUDIO_CHUNK"
                    )

                yield item

        finally:
            await worker_task


piper_tts = PiperTTSProvider()
