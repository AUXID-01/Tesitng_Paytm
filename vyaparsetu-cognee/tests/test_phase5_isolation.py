"""tests/test_phase5_isolation.py

Phase 5: Multi-Merchant Isolation Stress Test.
Attempts to induce cross-merchant data leakage.
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

SHARED_DATASET = "phase5_shared_isolation_test"
DATASET_MERCHANT_A = "phase5_merchant_sharma"
DATASET_MERCHANT_B = "phase5_merchant_gupta"

# Seed Data: Merchant A (Sharma) -> Suresh owes 200 INR
MERCHANT_A = {
    "merchant_id": "m_sharma_01",
    "shop_name": "Sharma Kirana Store",
    "owner_name": "Ramesh Sharma",
}
TXN_A = {
    "event_type": "customer_credit_log",
    "merchant_id": "m_sharma_01",
    "transaction_id": "txn_sharma_01",
    "customer": {
        "customer_id": "c_suresh_sharma",
        "name": "Suresh",
        "phone": "+919111111111",
    },
    "amount": 200.0,
    "items": ["Atta 5kg"],
    "timestamp": "2026-09-16T10:00:00Z",
}

# Seed Data: Merchant B (Gupta) -> Suresh owes 500 INR
MERCHANT_B = {
    "merchant_id": "m_gupta_02",
    "shop_name": "Gupta Provision Store",
    "owner_name": "Alok Gupta",
}
TXN_B = {
    "event_type": "customer_credit_log",
    "merchant_id": "m_gupta_02",
    "transaction_id": "txn_gupta_01",
    "customer": {
        "customer_id": "c_suresh_gupta",
        "name": "Suresh",
        "phone": "+919222222222",
    },
    "amount": 500.0,
    "items": ["Ghee 1L", "Dry Fruits"],
    "timestamp": "2026-09-16T10:30:00Z",
}


async def test_strategy_1_shared_dataset():
  print("\n" + "=" * 60)
  print("TESTING STRATEGY 1: Shared Dataset (Attempting Data Leak)")
  print("=" * 60)

  payload = (
      json.dumps(MERCHANT_A)
      + "\n\n"
      + json.dumps(TXN_A)
      + "\n\n"
      + json.dumps(MERCHANT_B)
      + "\n\n"
      + json.dumps(TXN_B)
  )

  await cognee.add(data=payload, dataset_name=SHARED_DATASET)
  await cognee.cognify(datasets=[SHARED_DATASET])

  # Adversarial query attempting to pull Merchant B's debt into Merchant A's scope
  leak_query = (
      "For merchant m_sharma_01 (Sharma Kirana Store), how much does customer"
      " Suresh owe? Do NOT include any other merchant."
  )
  print(f"\nRunning scoped query: '{leak_query}'")

  results = await cognee.search(query_text=leak_query)

  print("\n--- Strategy 1 Query Response ---")
  for r in results:
    ds_name = r.get("dataset_name") if isinstance(r, dict) else r.dataset_name
    if ds_name == SHARED_DATASET:
      res_text = (
          r.get("search_result") if isinstance(r, dict) else r.search_result
      )
      print(f"Result in shared dataset: {res_text}")

      # Assert lack of leakage
      text_str = str(res_text)
      if "500" in text_str or "Gupta" in text_str:
        print(
            "\n[!] ISOLATION FAILED: Merchant B's 500 INR or Gupta store"
            " leaked into Merchant A query!"
        )
      elif "200" in text_str:
        print("\n[+] ISOLATION PASSED: Only Merchant A's 200 INR was returned.")
      else:
        print("\n[?] Inconclusive response:", text_str)


async def test_strategy_2_dedicated_datasets():
  print("\n" + "=" * 60)
  print("TESTING STRATEGY 2: Dedicated Datasets per Merchant")
  print("=" * 60)

  # Ingest Merchant A into Dataset A
  payload_a = json.dumps(MERCHANT_A) + "\n\n" + json.dumps(TXN_A)
  await cognee.add(data=payload_a, dataset_name=DATASET_MERCHANT_A)
  await cognee.cognify(datasets=[DATASET_MERCHANT_A])

  # Ingest Merchant B into Dataset B
  payload_b = json.dumps(MERCHANT_B) + "\n\n" + json.dumps(TXN_B)
  await cognee.add(data=payload_b, dataset_name=DATASET_MERCHANT_B)
  await cognee.cognify(datasets=[DATASET_MERCHANT_B])

  print("\nQuerying ONLY Dataset A for Suresh's balance...")
  # Scoped strictly by dataset parameter if supported by search
  results_a = await cognee.search(
      query_text="How much does Suresh owe?", datasets=[DATASET_MERCHANT_A]
  )

  print("--- Strategy 2 Query Response ---")
  for r in results_a:
    ds_name = r.get("dataset_name") if isinstance(r, dict) else r.dataset_name
    if ds_name == DATASET_MERCHANT_A:
      print(f"Dataset A Output: {r}")


async def main():
  print("Connecting to Cognee Cloud...")
  await cognee.serve(url=TENANT_URL, api_key=API_KEY)

  await test_strategy_1_shared_dataset()
  await test_strategy_2_dedicated_datasets()

  await cognee.disconnect()


if __name__ == "__main__":
  asyncio.run(main())