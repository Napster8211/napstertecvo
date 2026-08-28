FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Install Python dependencies first so Docker can cache this layer.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Provision the verified Piper voice deterministically instead of relying on
# piper.download_voices' implicit download directory.
ARG PIPER_VOICE_NAME=en_US-lessac-medium
ARG PIPER_MODEL_SIZE=63201294
ARG PIPER_MODEL_SHA256=5EFE09E69902187827AF646E1A6E9D269DEE769F9877D17B16B1B46EEAAF019F
ARG PIPER_MODEL_URL=https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx?download=true
ARG PIPER_CONFIG_URL=https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json?download=true

ENV PIPER_VOICE_NAME=${PIPER_VOICE_NAME} \
    PIPER_VOICE_PATH=/opt/piper/voices/${PIPER_VOICE_NAME}.onnx \
    PIPER_SAMPLE_RATE=22050

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
    && python -c "import json; json.load(open('/opt/piper/voices/${PIPER_VOICE_NAME}.onnx.json', encoding='utf-8')); print('PIPER_CONFIG_OK')"

COPY app ./app

# Fail the image build if the application cannot import.
RUN python -c "from app.main import app; print('APPLICATION_IMPORT_OK')"

EXPOSE 8000

CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
