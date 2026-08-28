import os
os.environ["VOICE_GATEWAY_API_KEY"]="test-secret"
from app.config import get_settings
get_settings.cache_clear()
from fastapi.testclient import TestClient
from app.main import app
c=TestClient(app)
def test_health(): assert c.get("/health").status_code==200
def test_auth(): assert c.post("/api/v1/dnc/+233200000000").status_code in (401,403)
def test_approval():
    r=c.post("/api/v1/calls/outbound-lead",headers={"X-NapsterTec-Key":"test-secret"},json={"lead_id":"l1","recipient":"+233200000000","purpose":"intro","message":"hello","approved":False,"approval_reference":""})
    assert r.status_code==403
