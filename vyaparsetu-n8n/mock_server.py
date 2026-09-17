import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI()


class PayoutRequest(BaseModel):
  distributor_upi_id: str
  amount: float
  invoice_id: str


class CallbackRequest(BaseModel):
  invoice_id: str
  paid: bool
  payout_ref: str | None = None
  reason: str | None = None


@app.post("/mock/paytm/payout")
async def mock_payout(payload: PayoutRequest):
  # Failure Injection 1: Simulate Gateway Crash (500)
  if payload.invoice_id == "inv_chaos_500":
    raise HTTPException(
        status_code=500, detail="BANK_GATEWAY_INTERNAL_CRASH_SIMULATION"
    )

  # Failure Injection 2: Simulate Gateway Timeout (Hangs for 10 seconds)
  if payload.invoice_id == "inv_chaos_timeout":
    await asyncio.sleep(10)
    return {"status": "SUCCESS", "invoice_id": payload.invoice_id}

  # Normal Logic
  if payload.amount > 10000:
    return {
        "status": "FAILURE",
        "error_code": "INSUFFICIENT_FUNDS",
        "invoice_id": payload.invoice_id,
    }

  return {
      "status": "SUCCESS",
      "payout_ref": f"paytm_tx_{payload.invoice_id}",
      "invoice_id": payload.invoice_id,
  }


@app.post("/mock/vyaparsetu/callback")
def mock_callback(payload: CallbackRequest):
  print(f"\n[BACKEND CALLBACK RECEIVED] => {payload.model_dump()}")
  return {"acknowledged": True}


if __name__ == "__main__":
  uvicorn.run(app, host="0.0.0.0", port=8000)