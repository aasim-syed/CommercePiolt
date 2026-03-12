from typing import Any, Dict

from app.services.pine_labs import PineLabsClient

client = PineLabsClient()


async def create_payment_link(
    amount: float,
    merchant_id: str,
) -> Dict[str, Any]:

    return await client.create_payment_link(
        amount=amount,
        merchant_id=merchant_id,
    )