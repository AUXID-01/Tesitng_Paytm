import asyncio
import os
import time
import uuid
import cognee
from dotenv import load_dotenv
import sys
import io

# Force UTF-8 encoding for stdout to prevent UnicodeEncodeError on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Ensure memory module is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from memory.writers import write_transaction, write_invoice, write_settlement, write_merchant

load_dotenv()

TENANT_URL = os.getenv("COGNEE_TENANT_URL")
API_KEY = os.getenv("COGNEE_API_KEY")
DATASET_NAME = "phase3_verification_" + str(uuid.uuid4())[:8]

MERCHANT_ID = "m_sharma_01"

async def execute_step(step_name: str, write_coro, read_query: str = None):
    print(f"\n--- [{step_name}] ---")
    start_write = time.time()
    await write_coro
    latency_write = time.time() - start_write
    print(f"Write Latency: {latency_write:.2f}s")
    
    if read_query:
        print(f"Reading back -> Query: '{read_query}'")
        start_read = time.time()
        try:
            # Try standard Cognee search signature
            result = await cognee.search(query_text=read_query)
        except TypeError:
            try:
                # Fallback to positional argument
                result = await cognee.search(read_query)
            except Exception as e:
                result = f"Search Failed: {str(e)}"
        except Exception as e:
            result = f"Search Failed: {str(e)}"
        latency_read = time.time() - start_read
        print(f"Read Latency: {latency_read:.2f}s")
        print(f"Response:\n{result}\n")
    else:
        print("No read-back requested for this step.\n")

async def main():
    print(f"Connecting to Cognee Cloud... Target Dataset: {DATASET_NAME}")
    await cognee.serve(url=TENANT_URL, api_key=API_KEY)
    
    # 1. Merchant Setup
    await execute_step(
        "Merchant Setup",
        write_merchant(MERCHANT_ID, "Sharma Kirana Store", "Ramesh Sharma", DATASET_NAME),
        read_query="What is the shop name for m_sharma_01?"
    )

    # 2. Sequential Writes (10 Writes)
    # Write 1: Suresh owes 100
    suresh_data = {"customer_id": "c_suresh_01", "name": "Suresh", "phone": "+919876543210"}
    await execute_step(
        "Write 1 - Suresh Txn 1 (100 INR)",
        write_transaction(MERCHANT_ID, suresh_data, 100.0, ["Sugar 1kg"], "txn_001", DATASET_NAME),
        read_query="How much does Suresh owe in total? What are the transactions?"
    )

    # Write 2: Suresh owes 150
    await execute_step(
        "Write 2 - Suresh Txn 2 (150 INR)",
        write_transaction(MERCHANT_ID, suresh_data, 150.0, ["Rice 5kg"], "txn_002", DATASET_NAME),
        read_query="How much does Suresh owe now? Is it aggregated?"
    )

    # Write 3: Invoice 1
    dist_amul = {"distributor_id": "dist_001", "name": "Amul Sec 4", "upi_id": "amul@paytm"}
    await execute_step(
        "Write 3 - Amul Invoice",
        write_invoice(MERCHANT_ID, "inv_amul_01", dist_amul, [{"sku": "Milk", "quantity": 10, "unit_price": 30}], 300.0, DATASET_NAME),
        read_query="What invoices do we have for Amul?"
    )

    # Write 4: Settlement 1
    await execute_step(
        "Write 4 - Daily Settlement",
        write_settlement(MERCHANT_ID, "2026-09-15", 2500.0, 1000.0, 1500.0, DATASET_NAME),
        read_query=None
    )

    # Write 5: Ramesh Txn 1
    ramesh_data = {"customer_id": "c_ramesh_01", "name": "Ramesh", "phone": "+911122334455"}
    await execute_step(
        "Write 5 - Ramesh Txn 1",
        write_transaction(MERCHANT_ID, ramesh_data, 50.0, ["Soap"], "txn_003", DATASET_NAME),
        read_query="Who owes money to Sharma Kirana Store?"
    )

    # Write 6: Invoice 2
    dist_brit = {"distributor_id": "dist_002", "name": "Britannia Agency", "upi_id": "brit@paytm"}
    await execute_step(
        "Write 6 - Britannia Invoice",
        write_invoice(MERCHANT_ID, "inv_brit_01", dist_brit, [{"sku": "Biscuits", "quantity": 50, "unit_price": 10}], 500.0, DATASET_NAME),
        read_query=None
    )

    # Write 7: Settlement 2
    await execute_step(
        "Write 7 - Daily Settlement 2",
        write_settlement(MERCHANT_ID, "2026-09-16", 3000.0, 1200.0, 1800.0, DATASET_NAME),
        read_query=None
    )

    # Write 8: Suresh Txn 3 (Payment)
    await execute_step(
        "Write 8 - Suresh Payment",
        write_transaction(MERCHANT_ID, suresh_data, 100.0, [], "txn_004", DATASET_NAME), # Maybe negative for payment? 
        read_query="Has Suresh made any payments? What is his updated balance?"
    )

    # Write 9: Ramesh Txn 2
    await execute_step(
        "Write 9 - Ramesh Txn 2",
        write_transaction(MERCHANT_ID, ramesh_data, 20.0, ["Shampoo"], "txn_005", DATASET_NAME),
        read_query=None
    )

    # Write 10: Invoice 3
    await execute_step(
        "Write 10 - Amul Invoice 2",
        write_invoice(MERCHANT_ID, "inv_amul_02", dist_amul, [{"sku": "Butter", "quantity": 5, "unit_price": 50}], 250.0, DATASET_NAME),
        read_query="List all Amul invoices."
    )

    # 3. Entity Resolution Edge-Case Test
    print("\n=======================================================")
    print("--- [Entity Resolution Stress Test] ---")
    suresh_lowercase = {"customer_id": "c_suresh_02_unknown", "name": "suresh"} # lower case, no phone
    print("Writing transaction for customer named 'suresh' (lowercase) without phone number...")
    start_write = time.time()
    await write_transaction(MERCHANT_ID, suresh_lowercase, 300.0, ["Atta 10kg"], "txn_er_001", DATASET_NAME)
    print(f"Write Latency: {time.time() - start_write:.2f}s")
    
    print("Reading back to check if 'Suresh' and 'suresh' were unified...")
    start_read = time.time()
    query = "How many distinct customers named Suresh (case-insensitive) are there? Tell me the total debt for each."
    try:
        er_result = await cognee.search(query_text=query)
    except TypeError:
        er_result = await cognee.search(query)
    except Exception as e:
        er_result = f"Search Failed: {str(e)}"
        
    print(f"Read Latency: {time.time() - start_read:.2f}s")
    print(f"Response:\n{er_result}")
    print("=======================================================\n")
    print(f"Test complete. Please check the Cognee Cloud dashboard for dataset '{DATASET_NAME}'.")
    
    await cognee.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
