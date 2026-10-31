import hmac
import hashlib
from typing import Set
from fastapi import APIRouter, Header, HTTPException, Request, Response, status
from app.config import settings
from app.logging_config import logger

router = APIRouter(prefix="/v1/webhooks", tags = ["Webhooks"])

# in memory store for processed event IDs
processed_event_ids: Set[str] = set()

# simulated failure toggle (set to true to test sender retry behaviour)
SIMULATE_FAILURE: bool = False

def verify_github_signature(raw_body: bytes, signature_header: str) -> bool:
    """Verifies the HMAC-SHA256 signature sent by GitHub in X-Hub-Signature-256."""
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    
    expected_hash = hmac.new(
        key=settings.WEBHOOK_SECRET.encode("utf-8"),
        msg=raw_body,
        digestmod=hashlib.sha256
    ).hexdigest()
    
    received_hash = signature_header.split("sha256=")[1]
    
    # Constant-time comparison to prevent timing attacks
    return hmac.compare_digest(expected_hash, received_hash)

@router.post("/github", status_code=status.HTTP_200_OK)
async def github_webhook_receiver(
    request: Request,
    x_github_event: str = Header(None),
    x_github_delivery: str = Header(None),
    x_hub_signature_256: str = Header(None)
):
    # 1. Read Raw Body Bytes
    raw_body = await request.body()

    # 2. Signature Verification (Authenticity Check)
    if not x_hub_signature_256 or not verify_github_signature(raw_body, x_hub_signature_256):
        logger.warning(f"Invalid webhook signature for delivery: {x_github_delivery}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature"
        )

    # 3. Duplicate Detection / Idempotency Check
    if x_github_delivery in processed_event_ids:
        logger.info(f"Duplicate webhook event received: {x_github_delivery}. Skipping processing.")
        return Response(status_code=status.HTTP_200_OK, content="Event already processed")

    # 4. Failure Simulation Step (For testing retries)
    if SIMULATE_FAILURE:
        logger.error(f"Simulating internal error for webhook delivery: {x_github_delivery}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Simulated internal server error"
        )

    # 5. Process Payload (Parse JSON after verification)
    payload = await request.json()
    logger.info(f"Received valid GitHub event '{x_github_event}' (ID: {x_github_delivery})")

    # Record event ID to prevent duplicate execution
    processed_event_ids.add(x_github_delivery)

    # Return immediate acknowledgement
    return {
        "status": "success",
        "event": x_github_event,
        "delivery_id": x_github_delivery
    }