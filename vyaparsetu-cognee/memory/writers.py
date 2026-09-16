import json
import datetime
import cognee

async def write_merchant(merchant_id: str, shop_name: str, owner_name: str, dataset_name: str):
    payload = {
        "merchant_id": merchant_id,
        "shop_name": shop_name,
        "owner_name": owner_name,
    }
    json_data = json.dumps(payload, indent=2)
    await cognee.add(data=json_data, dataset_name=dataset_name)
    await cognee.cognify(datasets=[dataset_name])

async def write_transaction(merchant_id: str, customer_data: dict, amount: float, items: list[str], txn_id: str, dataset_name: str):
    payload = {
        "event_type": "customer_credit_log",
        "merchant_id": merchant_id,
        "intent": "add_credit",
        "transaction_id": txn_id,
        "customer": customer_data,
        "amount": amount,
        "currency": "INR",
        "items": items,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "confidence": 1.0,
        "source": "manual",
    }
    json_data = json.dumps(payload, indent=2)
    await cognee.add(data=json_data, dataset_name=dataset_name)
    await cognee.cognify(datasets=[dataset_name])

async def write_invoice(merchant_id: str, invoice_id: str, distributor_data: dict, line_items: list[dict], total_amount: float, dataset_name: str):
    payload = {
        "event_type": "distributor_delivery_challan",
        "merchant_id": merchant_id,
        "invoice_id": invoice_id,
        "distributor": distributor_data,
        "invoice_date": datetime.date.today().isoformat(),
        "line_items": line_items,
        "total_amount": total_amount,
        "paid": False,
    }
    json_data = json.dumps(payload, indent=2)
    await cognee.add(data=json_data, dataset_name=dataset_name)
    await cognee.cognify(datasets=[dataset_name])

async def write_settlement(merchant_id: str, date_str: str, upi_total: float, payout_total: float, net_balance: float, dataset_name: str):
    payload = {
        "event_type": "daily_settlement_rollup",
        "merchant_id": merchant_id,
        "date": date_str,
        "upi_collection_total": upi_total,
        "supplier_payout_total": payout_total,
        "net_balance": net_balance,
    }
    json_data = json.dumps(payload, indent=2)
    await cognee.add(data=json_data, dataset_name=dataset_name)
    await cognee.cognify(datasets=[dataset_name])
