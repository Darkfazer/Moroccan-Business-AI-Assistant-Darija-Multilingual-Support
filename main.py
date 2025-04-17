from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from ai_service import AIService  # Your AI service
from database import Database    # Your database handler

# Initialize FastAPI app (THIS MUST BE NAMED 'app')
app = FastAPI(title="Morocco AI Agent")

# Add CORS if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
db = Database()
ai = AIService()

class ChatRequest(BaseModel):
    message: str
    business_id: str = "default_shop"

@app.on_event("startup")
async def startup():
    await db.connect()

@app.post("/chat")
async def handle_chat(request: ChatRequest):
    """Main endpoint for chat requests"""
    business = await db.get_business(request.business_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    response = await ai.generate_response(request.message, business)
    await db.log_conversation(request.business_id, request.message, response)
    
    return {"reply": response}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Only for development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)