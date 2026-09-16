"""memory/schema.py

Defines every node and edge type stored in Cognee for VyaparSetu.
Inherits from cognee.infrastructure.engine.DataPoint to bind directly
to Cognee's graph storage engine.
"""

from datetime import datetime
from typing import List, Literal, Optional
from cognee.infrastructure.engine import DataPoint


class Merchant(DataPoint):
  merchant_id: str
  shop_name: str
  owner_name: str
  metadata: dict = {"index_fields": ["merchant_id"]}


class Customer(DataPoint):
  customer_id: str
  merchant_id: str
  name: str
  phone: Optional[str] = None
  owes: Optional[Merchant] = None  # Edge: Customer -> OWES -> Merchant
  metadata: dict = {"index_fields": ["customer_id", "merchant_id"]}


class Transaction(DataPoint):
  txn_id: str
  merchant_id: str
  customer_id: str
  amount: float
  items: List[str]
  txn_type: Literal["credit_added", "credit_paid"]
  timestamp: datetime
  source: Literal["voice", "manual"]
  confidence: float
  logged_by: Optional[Merchant] = None  # Edge: Transaction -> LOGGED_BY -> Merchant
  metadata: dict = {"index_fields": ["txn_id", "merchant_id", "customer_id"]}


class Distributor(DataPoint):
  distributor_id: str
  merchant_id: str
  name: str
  upi_id: str
  metadata: dict = {"index_fields": ["distributor_id", "merchant_id"]}


class LineItem(DataPoint):
  sku: str
  quantity: int
  unit_price: float
  metadata: dict = {"index_fields": ["sku"]}


class Invoice(DataPoint):
  invoice_id: str
  merchant_id: str
  distributor_id: str
  invoice_date: datetime
  total_amount: float
  paid: bool = False
  supplied_by: Optional[Distributor] = (
      None  # Edge: Invoice -> SUPPLIED_BY -> Distributor
  )
  contains: Optional[List[LineItem]] = (
      None  # Edge: Invoice -> CONTAINS -> LineItem
  )
  metadata: dict = {"index_fields": ["invoice_id", "merchant_id"]}


class SettlementRecord(DataPoint):
  merchant_id: str
  date: datetime
  upi_collection_total: float
  payout_total: float
  net_balance: float
  metadata: dict = {"index_fields": ["merchant_id", "date"]}