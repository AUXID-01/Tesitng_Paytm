import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

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


# Mock Paytm Settlement Payout Endpoint
@app.post("/mock/paytm/payout")
def mock_payout(payload: PayoutRequest):
  # Force failure if amount is over 10,000 INR (for easy failure branch testing)
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
      "amount": payload.amount,
  }


# Mock FastAPI Callback Endpoint
@app.post("/mock/vyaparsetu/callback")
def mock_callback(payload: CallbackRequest):
  print(f"\n[BACKEND CALLBACK RECEIVED] => {payload.model_dump()}")
  return {"acknowledged": True}


if __name__ == "__main__":
  uvicorn.run(app, host="0.0.0.0", port=8000)