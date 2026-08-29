FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ARG PIPER_VOICE_NAME=en_US-lessac-low
ARG PIPER_MODEL_SIZE=63201294
ARG PIPER_MODEL_SHA256=F7D01DDE371555732C4C314111AC79672B1A5CE2FC19266AB42178FD8DF7F375
ARG PIPER_MODEL_URL=https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/low/en_US-lessac-low.onnx?download=true
ARG PIPER_CONFIG_URL=https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/low/en_US-lessac-low.onnx.json?download=true

ENV PIPER_VOICE_NAME=${PIPER_VOICE_NAME} \
    PIPER_VOICE_PATH=/opt/piper/voices/${PIPER_VOICE_NAME}.onnx \
    PIPER_SAMPLE_RATE=16000

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/piper/voices \
    && curl -LfsS --retry 3 --retry-delay 2 \
       "${PIPER_MODEL_URL}" \
       -o "/opt/piper/voices/${PIPER_VOICE_NAME}.onnx" \
    && curl -LfsS --retry 3 --retry-delay 2 \
       "${PIPER_CONFIG_URL}" \
       -o "/opt/piper/voices/${PIPER_VOICE_NAME}.onnx.json" \
    && test "$(stat -c%s "/opt/piper/voices/${PIPER_VOICE_NAME}.onnx")" -eq "${PIPER_MODEL_SIZE}" \
    && echo "${PIPER_MODEL_SHA256}  /opt/piper/voices/${PIPER_VOICE_NAME}.onnx" | sha256sum -c - \
    && python -c "import json; c=json.load(open('/opt/piper/voices/${PIPER_VOICE_NAME}.onnx.json', encoding='utf-8')); assert c['audio']['sample_rate'] == 16000; print('PIPER_CONFIG_OK')"

COPY app ./app

RUN python -c "from app.main import app; print('APPLICATION_IMPORT_OK')"

EXPOSE 8000

CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
