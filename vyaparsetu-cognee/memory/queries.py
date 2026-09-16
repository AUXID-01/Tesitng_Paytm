"""memory/queries.py

Phase 4: The Three Core Queries.
Implements retrieval functions for:
1. Customer outstanding balance
2. Historical distributor SKU rate audit
3. Daily settlement rollup
"""

import asyncio
import os
import cognee
from dotenv import load_dotenv

load_dotenv()

TENANT_URL = os.getenv("COGNEE_TENANT_URL")
API_KEY = os.getenv("COGNEE_API_KEY")


async def get_customer_due(customer_name: str, merchant_id: str):
  """Query 1: Customer outstanding due."""
  query = f"For merchant {merchant_id}, how much total credit does {customer_name} owe? List the itemized transactions."
  return await cognee.search(query_text=query)


async def get_rate_history(sku: str, distributor_name: str):
  """Query 2: Historical SKU rate audit."""
  query = f"What is the historical unit price history for '{sku}' supplied by '{distributor_name}'? Compare the latest price to the previous price."
  return await cognee.search(query_text=query)


async def get_daily_summary(date_str: str, merchant_id: str):
  """Query 3: Daily collection and payout summary."""
  query = f"What was the UPI collection total, supplier payout total, and net balance for merchant {merchant_id} on {date_str}?"
  return await cognee.search(query_text=query)