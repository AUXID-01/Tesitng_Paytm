"""tests/test_phase4_queries.py

Runs Phase 4 validation against dataset: phase2_json_run
Compares Cognee retrieval output to known ground truth values.
"""

import asyncio
import os
import sys
import cognee
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from memory.queries import get_customer_due, get_daily_summary, get_rate_history

load_dotenv()

TARGET_DATASET = "phase2_json_run"


async def main():
  await cognee.serve(
      url=os.getenv("COGNEE_TENANT_URL"), api_key=os.getenv("COGNEE_API_KEY")
  )

  print("\n" + "=" * 60)
  print("--- BENCHMARK 1: Customer Outstanding Due ---")
  print("Expected: 300.0 INR (240 + 60)")
  print("=" * 60)
  res1 = await get_customer_due("Suresh", "m_sharma_01")
  for r in res1:
    if r.get("dataset_name") == TARGET_DATASET:
      print("Cognee Output:\n", r.get("search_result"))

  print("\n" + "=" * 60)
  print("--- BENCHMARK 2: SKU Rate Audit ---")
  print("Expected: 27.0 INR on 2026-09-01 -> 28.5 INR on 2026-09-16 (Delta: +1.5 INR)")
  print("=" * 60)
  res2 = await get_rate_history("Dahi 200g pouch", "Amul Distributor - Sector 4")
  for r in res2:
    if r.get("dataset_name") == TARGET_DATASET:
      print("Cognee Output:\n", r.get("search_result"))

  print("\n" + "=" * 60)
  print("--- BENCHMARK 3: Daily Settlement Rollup ---")
  print(
      "Expected: Collection: 6200.0, Payout: 3850.0, Net Balance: 2350.0 on"
      " 2026-09-16"
  )
  print("=" * 60)
  res3 = await get_daily_summary("2026-09-16", "m_sharma_01")
  for r in res3:
    if r.get("dataset_name") == TARGET_DATASET:
      print("Cognee Output:\n", r.get("search_result"))

  await cognee.disconnect()


if __name__ == "__main__":
  asyncio.run(main())