# whatsapp_webhook.py
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import httpx

router = APIRouter()

@router.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    data = await request.json()
    
    # Extract message from WhatsApp payload
    message = data.get("messages", [{}])[0].get("text", {}).get("body", "")
    phone_number = data.get("messages", [{}])[0].get("from", "")
    
    if not message:
        return JSONResponse({"status": "ignored"})
    
    # Process through backend
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/chat",
            json={
                "message": message,
                "business_id": "shop1"  # Would come from mapping phone number to business
            }
        )
    
    # Send reply back to WhatsApp
    reply = response.json().get("reply", "Désolé, une erreur s'est produite.")
    await send_whatsapp_message(phone_number, reply)
    
    return JSONResponse({"status": "processed"})

async def send_whatsapp_message(to: str, message: str):
    # Implementation would use Twilio or WhatsApp Business API
    print(f"[WhatsApp] Sending to {to}: {message}")
    return True