# BCO Demo Basket Bot — Railway Project

Standalone OANDA **practice-account** forward test for Brent (`BCO_USD`) using the Project Exit Plan basket architecture.

## Frozen test specification

- BCO long only
- 1H execution / 8H context
- broad `trend_long_v1` candidate
- every accepted hourly signal may open another trade
- no strategy cooldown or trade-count cap
- fixed £5-equivalent risk target per trade for the initial demo
- 3.5% emergency stop
- minimum 48-hour hold
- hourly basket management after 48 hours
- 72h / 96h / 120h extension and managed-stop milestones
- separate OIL_BASKET
- DAX and US30 excluded from the dashboard research scope

## Files

- `app.py` — complete application
- `requirements.txt` — Python dependencies
- `railway.json` — Railway build/start/health configuration
- `railway_variables_SAFE_START.txt` — variables for the first locked deployment
- `ENABLE_BCO_DEMO_AFTER_CHECKS.txt` — the two changes that unlock practice orders
- `tradingview_bco_alert_example.json` — minimum compatible alert payload
- `smoke_test_webhook.py` — optional candidate=false webhook test

## Deployment order

### 1. Create the new Railway project

Create a new Railway project and deploy this folder through GitHub or the Railway CLI. Railway will start the app with:

`uvicorn app:app --host 0.0.0.0 --port $PORT`

### 2. Add persistent storage

Add a Railway volume and mount it at:

`/data`

The SQLite database will be stored at:

`/data/bco_demo.sqlite`

Do not deploy without the volume if you want the forward-test history to survive rebuilds.

### 3. Paste the safe-start variables

Copy all entries from `railway_variables_SAFE_START.txt` into Railway Variables.

Replace:

- `<create-a-new-bco-webhook-secret>`
- `<copy-demo-account-id>`
- `<newly-rotated-demo-token>`

The initial variables deliberately use:

- `BROKER_EXECUTION_ENABLED=false`
- `BROKER_KILL_SWITCH=true`

Therefore the first deployment cannot send an order.

### 4. Generate a public domain

Generate a Railway domain for the service.

Check:

- `/health`
- `/dashboard`
- `/broker/oanda/instruments`
- `/broker/oanda/safety`

Confirm that:

- OANDA environment is `practice`
- the intended demo account is connected
- `BCO_USD` appears in the account instrument list
- the service scope shows only `BCO_USD`
- broker orders are still blocked

### 5. Run the safe webhook smoke test

Either send a candidate=false alert from TradingView or run:

```bash
BCO_BASE_URL=https://YOUR-RAILWAY-DOMAIN \
BCO_WEBHOOK_SECRET=YOUR-SECRET \
python smoke_test_webhook.py
```

It should store one BCO raw signal without creating an OANDA trade.

### 6. Unlock the practice account

Only after the checks pass, change the two variables shown in `ENABLE_BCO_DEMO_AFTER_CHECKS.txt`:

- `BROKER_EXECUTION_ENABLED=true`
- `BROKER_KILL_SWITCH=false`

Redeploy and re-check `/broker/oanda/safety`.

### 7. Create the live TradingView alert

Webhook URL:

`https://YOUR-RAILWAY-DOMAIN/webhook/tradingview`

Use the real BCO indicator output, not the placeholder booleans in the example JSON. The managed engine accepts only the frozen 1H/8H long candidate. The 1H/12H pullback challenger may remain logged for research but cannot open a managed trade.

## First real candidate checks

After the first candidate=true BCO signal, confirm all of the following:

1. The raw signal appears in the dashboard.
2. One shadow trade is created.
3. One OANDA practice trade is linked.
4. Instrument is `BCO_USD`.
5. An immediate 3.5% emergency stop exists and is rebased to the actual fill.
6. No NAS100, US500, DAX or US30 order is possible from this service.
7. A second accepted hourly candidate can create a second BCO trade.

## Security

The OANDA token previously pasted into chat should be revoked and replaced before this project is enabled. Never commit `.env` or real credentials to GitHub.
