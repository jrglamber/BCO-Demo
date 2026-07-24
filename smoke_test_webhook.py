"""Optional local/remote webhook smoke test.

Usage:
  BCO_BASE_URL=https://your-service.up.railway.app \
  BCO_WEBHOOK_SECRET=your-secret \
  python smoke_test_webhook.py

The payload is candidate=false, so it should be stored but must not place an order.
"""
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

base = os.getenv("BCO_BASE_URL", "").rstrip("/")
secret = os.getenv("BCO_WEBHOOK_SECRET", "")
if not base or not secret:
    raise SystemExit("Set BCO_BASE_URL and BCO_WEBHOOK_SECRET first.")

now = datetime.now(timezone.utc).isoformat()
payload = {
    "secret": secret,
    "source": "manual_safe_smoke_test",
    "pair": "BCOUSD",
    "signal_id": f"BCO_SAFE_SMOKE_{now}",
    "timestamp": now,
    "timeframe": "1H",
    "execution_tf": "1H",
    "context_tf": "8H",
    "signal_side": "long",
    "exec_close": 80.0,
    "exec_high": 80.2,
    "exec_low": 79.8,
    "forward_test_candidate": "false",
    "rule_trend_long_v1": "false",
    "model_version": "BCO_1H_8H_TREND_LONG_V1",
}
req = urllib.request.Request(
    f"{base}/webhook/tradingview",
    data=json.dumps(payload).encode("utf-8"),
    method="POST",
    headers={"Content-Type": "application/json"},
)
try:
    with urllib.request.urlopen(req, timeout=20) as response:
        body = response.read().decode("utf-8")
        print(response.status)
        print(body)
except urllib.error.HTTPError as exc:
    print(exc.code, exc.read().decode("utf-8", errors="replace"), file=sys.stderr)
    raise
