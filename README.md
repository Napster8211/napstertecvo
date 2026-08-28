# NapsterTec Voice Gateway

Standalone voice/telephony infrastructure for NapsterTec AI. Keep this project separate from the main NIE backend.

## Scope
- Piper self-hosted TTS.
- Raw PCM streaming plus WAV compatibility.
- Arkesel Voice SMS outbound adapter.
- Safe integration boundary for Arkesel VoiceConnect inbound/outbound live calls.
- Receptionist/call-event bridge back to NIE Communication Intelligence.
- Approval and local Do-Not-Call checks for outbound lead calls.

## Arkesel boundary
Arkesel publicly advertises Voice SMS, inbound/outbound VoiceConnect, IVR, browser softphones, outbound dialling, webhooks, AI voice agents and Enterprise API access. The exact VoiceConnect media/call-control API is not assumed here. `arkesel_voiceconnect.py` must only be completed from NapsterTec's official Arkesel VoiceConnect contract/docs.

Official references:
https://arkesel.com/developer-api/
https://arkesel.com/voice-sms/
https://arkesel.com/voice-connect/
https://arkesel.com/voice-connect/ghana/

## Architecture
NIE Communication Intelligence -> Voice Gateway -> Piper / Arkesel
Arkesel inbound webhook -> Voice Gateway -> NIE Communication Intelligence

## Run
Copy `.env.example` to `.env`, then:
`pip install -r requirements.txt`
`uvicorn app.main:app --host 0.0.0.0 --port 8000`

All `/api/v1/*` routes require `X-NapsterTec-Key`.
