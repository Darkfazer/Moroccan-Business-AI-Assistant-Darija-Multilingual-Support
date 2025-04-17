# database.py
import asyncpg
from fastapi import HTTPException
from typing import Optional
import os

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            host=os.getenv("DB_HOST")
        )

    async def get_business(self, business_id: str) -> Optional[dict]:
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT * FROM businesses WHERE id = $1", business_id
                )
                return dict(row) if row else None
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    async def log_conversation(self, business_id: str, message: str, response: str):
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    """INSERT INTO conversations 
                    (business_id, customer_message, ai_response)
                    VALUES ($1, $2, $3)""",
                    business_id, message, response
                )
        except Exception as e:
            print(f"Failed to log conversation: {str(e)}")