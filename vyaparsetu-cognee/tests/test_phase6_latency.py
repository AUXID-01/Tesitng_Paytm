"""
tests/test_phase6_latency.py

Phase 6: Latency and Duplicate-Write Stress Test.
Fires 10 sequential writes simulating a busy kirana counter,
benchmarks add, cognify, and search times individually,
and detects any stale read occurrences.
"""

import os
import sys
import time
import json
import asyncio
import cognee
from dotenv import load_dotenv

load_dotenv()

TENANT_URL = os.getenv("COGNEE_TENANT_URL")
API_KEY = os.getenv("COGNEE_API_KEY")

DATASET_NAME = f"phase6_load_test_{int(time.time())}"
MERCHANT_ID = "m_sharma_01"


async def main():
    print(f"Connecting to Cognee Cloud... Target Dataset: {DATASET_NAME}")
    await cognee.serve(url=TENANT_URL, api_key=API_KEY)

    # Initial Merchant Seed
    merchant_payload = json.dumps({
        "merchant_id": MERCHANT_ID,
        "shop_name": "Sharma Kirana Store",
        "owner_name": "Ramesh Sharma"
    })
    await cognee.add(data=merchant_payload, dataset_name=DATASET_NAME)
    await cognee.cognify(datasets=[DATASET_NAME])

    latencies = []
    running_expected_balance = 0.0

    print("\n" + "=" * 70)
    print("STARTING RAPID WRITE SEQUENCE (10 Sequential Transactions)")
    print("=" * 70)

    for i in range(1, 11):
        txn_amount = 50.0
        running_expected_balance += txn_amount
        txn_id = f"txn_load_{i:03d}"

        txn_payload = json.dumps({
            "event_type": "customer_credit_log",
            "merchant_id": MERCHANT_ID,
            "transaction_id": txn_id,
            "customer": {
                "customer_id": "c_vikram_01",
                "name": "Vikram",
                "phone": "+919811122233"
            },
            "amount": txn_amount,
            "currency": "INR",
            "items": [f"Item Batch {i}"],
            "timestamp": f"2026-09-16T14:{i:02d}:00Z"
        })

        print(f"\n[Write {i:02d}/10] Appending {txn_id} (+{txn_amount} INR)...")

        # 1. Measure add()
        t0 = time.perf_counter()
        await cognee.add(data=txn_payload, dataset_name=DATASET_NAME)
        t_add = time.perf_counter() - t0

        # 2. Measure cognify()
        t1 = time.perf_counter()
        await cognee.cognify(datasets=[DATASET_NAME])
        t_cognify = time.perf_counter() - t1

        # 3. Measure immediate read-back via search()
        query = f"For merchant {MERCHANT_ID}, what is the total amount owed by Vikram?"
        t2 = time.perf_counter()
        search_res = await cognee.search(query_text=query)
        t_read = time.perf_counter() - t2

        total_turnaround = t_add + t_cognify + t_read

        # Extract answer snippet for active dataset
        snippet = ""
        for r in search_res:
            ds = r.get("dataset_name") if isinstance(r, dict) else getattr(r, "dataset_name", "")
            if ds == DATASET_NAME:
                snippet = str(r.get("search_result") if isinstance(r, dict) else getattr(r, "search_result", ""))
                break

        # Check for stale read (balance mismatch)
        stale = str(int(running_expected_balance)) not in snippet and str(running_expected_balance) not in snippet

        latencies.append({
            "run": i,
            "add_s": round(t_add, 2),
            "cognify_s": round(t_cognify, 2),
            "read_s": round(t_read, 2),
            "total_s": round(total_turnaround, 2),
            "expected_balance": running_expected_balance,
            "stale": stale
        })

        status_marker = "[STALE READ]" if stale else "[FRESH]"
        print(f" -> Add: {t_add:.2f}s | Cognify: {t_cognify:.2f}s | Read: {t_read:.2f}s | Total: {total_turnaround:.2f}s | {status_marker}")
        print(f"    Expected: {running_expected_balance} INR | Cognee Answer Snippet: {snippet[:90]}...")

    # Summary Report
    print("\n" + "=" * 70)
    print("PHASE 6 BENCHMARK REPORT")
    print("=" * 70)
    print(f"{'Run':<5}{'Add (s)':<10}{'Cognify (s)':<14}{'Read (s)':<12}{'Total (s)':<12}{'Status'}")
    print("-" * 65)
    for row in latencies:
        print(f"{row['run']:<5}{row['add_s']:<10}{row['cognify_s']:<14}{row['read_s']:<12}{row['total_s']:<12}{'STALE' if row['stale'] else 'OK'}")

    avg_cognify = sum(r["cognify_s"] for r in latencies) / len(latencies)
    avg_read = sum(r["read_s"] for r in latencies) / len(latencies)
    avg_total = sum(r["total_s"] for r in latencies) / len(latencies)

    print("-" * 65)
    print(f"Average Cognify Indexing Time : {avg_cognify:.2f}s")
    print(f"Average Search/Recall Time    : {avg_read:.2f}s")
    print(f"Average End-to-End Turnaround : {avg_total:.2f}s")

    await cognee.disconnect()


if __name__ == "__main__":
    asyncio.run(main())