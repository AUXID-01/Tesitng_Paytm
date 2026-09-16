"""tests/seed_phase2.py

Seeds structured JSON payloads matching the output schemas of:
1. Voice Khata (credit logging)
2. Delivery Challan Lens (distributor invoices)
3. Daily Settlement Summary
"""

import asyncio
import json
import os
import sys
import cognee
from dotenv import load_dotenv

load_dotenv()

TENANT_URL = os.getenv("COGNEE_TENANT_URL")
API_KEY = os.getenv("COGNEE_API_KEY")

# Merchant Context
MERCHANT = {
    "merchant_id": "m_sharma_01",
    "shop_name": "Sharma Kirana Store",
    "owner_name": "Ramesh Sharma",
}

# 1. Voice Khata Output (Flow A3: Entity Extraction LLM output)
VOICE_KHATA_TXN_1 = {
    "event_type": "customer_credit_log",
    "merchant_id": "m_sharma_01",
    "intent": "add_credit",
    "transaction_id": "txn_101",
    "customer": {
        "customer_id": "c_suresh_01",
        "name": "Suresh",
        "phone": "+919876543210",
    },
    "amount": 240.0,
    "currency": "INR",
    "items": ["Dahi 200g pouch", "Refined Oil 1L"],
    "timestamp": "2026-09-14T10:30:00Z",
    "confidence": 0.94,
    "source": "voice",
}

VOICE_KHATA_TXN_2 = {
    "event_type": "customer_credit_log",
    "merchant_id": "m_sharma_01",
    "intent": "add_credit",
    "transaction_id": "txn_102",
    "customer": {
        "customer_id": "c_suresh_01",
        "name": "Suresh",
        "phone": "+919876543210",
    },
    "amount": 60.0,
    "currency": "INR",
    "items": ["Dahi 200g pouch"],
    "timestamp": "2026-09-15T11:00:00Z",
    "confidence": 0.91,
    "source": "voice",
}

# 2. Challan Lens Output (Flow B2: Vision Extraction LLM output)
CHALLAN_INVOICE_OLD = {
    "event_type": "distributor_delivery_challan",
    "merchant_id": "m_sharma_01",
    "invoice_id": "inv_amul_001",
    "distributor": {
        "distributor_id": "dist_amul_sec4",
        "name": "Amul Distributor - Sector 4",
        "upi_id": "amuldist4@paytm",
    },
    "invoice_date": "2026-09-01",
    "line_items": [
        {"sku": "Dahi 200g pouch", "quantity": 50, "unit_price": 27.00}
    ],
    "total_amount": 1350.0,
    "paid": True,
}

CHALLAN_INVOICE_NEW = {
    "event_type": "distributor_delivery_challan",
    "merchant_id": "m_sharma_01",
    "invoice_id": "inv_amul_002",
    "distributor": {
        "distributor_id": "dist_amul_sec4",
        "name": "Amul Distributor - Sector 4",
        "upi_id": "amuldist4@paytm",
    },
    "invoice_date": "2026-09-16",
    "line_items": [
        {"sku": "Dahi 200g pouch", "quantity": 50, "unit_price": 28.50}
    ],
    "total_amount": 1425.0,
    "paid": False,
}

# 3. Grounded Q&A Settlement (Flow C3)
SETTLEMENT_RECORD = {
    "event_type": "daily_settlement_rollup",
    "merchant_id": "m_sharma_01",
    "date": "2026-09-16",
    "upi_collection_total": 6200.0,
    "supplier_payout_total": 3850.0,
    "net_balance": 2350.0,
}


async def seed(dataset_name: str):
  print(f"Connecting to Cognee Cloud for dataset: {dataset_name}...")
  await cognee.serve(url=TENANT_URL, api_key=API_KEY)

  # Package all structured events into clean formatted JSON blocks
  payload_items = [
      MERCHANT,
      VOICE_KHATA_TXN_1,
      VOICE_KHATA_TXN_2,
      CHALLAN_INVOICE_OLD,
      CHALLAN_INVOICE_NEW,
      SETTLEMENT_RECORD,
  ]

  # Serialize each structured event to formatted JSON
  json_data = "\n\n".join(
      [json.dumps(item, indent=2) for item in payload_items]
  )

  print(
      f"Ingesting {len(payload_items)} structured JSON payloads into"
      f" '{dataset_name}'..."
  )
  await cognee.add(data=json_data, dataset_name=dataset_name)

  print(f"Running cognify() on '{dataset_name}'...")
  await cognee.cognify(datasets=[dataset_name])

  print(f"Dataset '{dataset_name}' successfully processed.")
  await cognee.disconnect()


if __name__ == "__main__":
  target = sys.argv[1] if len(sys.argv) > 1 else "phase2_json_run"
  asyncio.run(seed(target))