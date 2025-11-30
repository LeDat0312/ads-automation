"""
Facebook Webhook Router
Handle webhook verification and incoming events from Facebook
"""
from fastapi import APIRouter, Request, Query, HTTPException
from typing import Optional
import logging
import hmac
import hashlib

from app.core.config import get_settings

router = APIRouter(prefix="/api/facebook", tags=["facebook-webhook"])
logger = logging.getLogger(__name__)
settings = get_settings()


@router.get("/webhook")
async def verify_facebook_webhook(
    hub_mode: Optional[str] = Query(None, alias="hub.mode"),
    hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token"),
    hub_challenge: Optional[str] = Query(None, alias="hub.challenge")
):
    """
    Verify Facebook webhook endpoint
    
    Facebook will send GET request with:
    - hub.mode=subscribe
    - hub.verify_token=<your_verify_token>
    - hub.challenge=<random_string>
    
    Must respond with hub.challenge if verification succeeds
    
    Query params:
        hub.mode: Should be "subscribe"
        hub.verify_token: Must match FACEBOOK_VERIFY_TOKEN in settings
        hub.challenge: Random string to echo back
    """
    logger.info(f"🔔 Webhook verification request: mode={hub_mode}, token={hub_verify_token}")
    
    # Verify all required parameters are present
    if not hub_mode or not hub_verify_token or not hub_challenge:
        logger.error("❌ Missing required webhook verification parameters")
        raise HTTPException(status_code=400, detail="Missing verification parameters")
    
    # Verify mode is "subscribe"
    if hub_mode != "subscribe":
        logger.error(f"❌ Invalid hub.mode: {hub_mode}")
        raise HTTPException(status_code=403, detail="Invalid mode")
    
    # Verify token matches configured token
    if hub_verify_token != settings.FACEBOOK_VERIFY_TOKEN:
        logger.error(f"❌ Invalid verify token: {hub_verify_token}")
        raise HTTPException(status_code=403, detail="Invalid verify token")
    
    logger.info(f"✅ Webhook verification successful")
    
    # Return challenge to complete verification
    return int(hub_challenge)


@router.post("/webhook")
async def receive_facebook_webhook(request: Request):
    """
    Receive webhook events from Facebook
    
    Events include:
    - feed: New posts on page
    - comments: New comments on posts
    - messages: New messages in Messenger
    - leadgen: New leads from lead forms
    - messaging_postbacks: Button clicks in Messenger
    
    Facebook sends POST requests with:
    - X-Hub-Signature-256: HMAC SHA256 signature for validation
    - Body: JSON with entries array
    
    Response:
        Must return 200 OK within 20 seconds or Facebook will retry
    """
    # Get request body
    body = await request.body()
    
    # Verify signature
    signature_header = request.headers.get("X-Hub-Signature-256", "")
    
    if signature_header:
        # Extract signature (format: "sha256=<signature>")
        try:
            signature = signature_header.split("sha256=")[1]
        except IndexError:
            logger.error("❌ Invalid signature header format")
            raise HTTPException(status_code=401, detail="Invalid signature format")
        
        # Calculate expected signature
        expected_signature = hmac.new(
            key=settings.FACEBOOK_APP_SECRET.encode(),
            msg=body,
            digestmod=hashlib.sha256
        ).hexdigest()
        
        # Compare signatures
        if not hmac.compare_digest(signature, expected_signature):
            logger.error("❌ Signature verification failed")
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        logger.info("✅ Webhook signature verified")
    else:
        logger.warning("⚠️ No signature header found (may be test event)")
    
    # Parse JSON body
    try:
        data = await request.json()
    except Exception as e:
        logger.error(f"❌ Failed to parse JSON body: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    # Log event
    logger.info(f"🔔 Webhook event received: {data.get('object', 'unknown')}")
    
    # Process entries
    entries = data.get("entry", [])
    
    for entry in entries:
        page_id = entry.get("id")
        time = entry.get("time")
        
        logger.info(f"📄 Processing entry for page {page_id} at {time}")
        
        # Process changes/messaging events
        changes = entry.get("changes", [])
        messaging = entry.get("messaging", [])
        
        # Handle feed/comment changes
        for change in changes:
            field = change.get("field")
            value = change.get("value")
            
            logger.info(f"  🔹 Change: {field}")
            
            # TODO: Implement handlers for different fields
            if field == "feed":
                # New post on page
                logger.info(f"    📝 New feed post: {value}")
                # Handle new post
                
            elif field == "comments":
                # New comment on post
                logger.info(f"    💬 New comment: {value}")
                # Handle new comment
                
            elif field == "leadgen":
                # New lead from lead form
                logger.info(f"    🎯 New lead: {value}")
                # Handle new lead
        
        # Handle messaging events
        for message_event in messaging:
            sender_id = message_event.get("sender", {}).get("id")
            recipient_id = message_event.get("recipient", {}).get("id")
            
            logger.info(f"  🔹 Message event: sender={sender_id}, recipient={recipient_id}")
            
            # Message event
            if "message" in message_event:
                message = message_event["message"]
                logger.info(f"    💬 Message: {message.get('text', 'no text')}")
                # TODO: Handle incoming message
            
            # Postback event (button click)
            elif "postback" in message_event:
                postback = message_event["postback"]
                logger.info(f"    🔘 Postback: {postback.get('payload', 'no payload')}")
                # TODO: Handle button click
    
    logger.info(f"✅ Webhook event processed ({len(entries)} entries)")
    
    # Must return 200 OK
    return {"status": "ok"}
