from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from contextlib import asynccontextmanager
import redis.asyncio as redis
import json

from src.database import get_db, init_db
from src.schemas import ContentSubmitRequest, ContentResponse, StatusResponse
from src.models import Content, ModerationResult
from src.services.rate_limiter import RateLimiter
from src.config import settings

# Lifetime manager to init DB on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)
rate_limiter = RateLimiter(settings.REDIS_URL)
redis_client = redis.from_url(settings.REDIS_URL)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/api/v1/content/submit", response_model=ContentResponse, status_code=202)
async def submit_content(
    payload: ContentSubmitRequest, 
    db: AsyncSession = Depends(get_db)
):
    # 1. Rate Limiting
    if not await rate_limiter.is_allowed(payload.userId):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, 
            detail="Rate limit exceeded. Please try again later."
        )

    # 2. Persist Initial Data (Transactional)
    new_content = Content(user_id=payload.userId, text=payload.text)
    db.add(new_content)
    await db.flush() # Generate ID
    
    # Init moderation status
    mod_result = ModerationResult(content_id=new_content.id, status="PENDING")
    db.add(mod_result)
    await db.commit()

    # 3. Publish Event (Using Redis List as a reliable Queue)
    event = {
        "contentId": str(new_content.id),
        "text": payload.text,
        "userId": payload.userId
    }
    await redis_client.rpush(settings.QUEUE_NAME, json.dumps(event))

    return {"contentId": new_content.id}

@app.get("/api/v1/content/{content_id}/status", response_model=StatusResponse)
async def get_status(content_id: str, db: AsyncSession = Depends(get_db)):
    try:
        query = select(ModerationResult).where(ModerationResult.content_id == content_id)
        result = await db.execute(query)
        record = result.scalar_one_or_none()
        
        if not record:
            raise HTTPException(status_code=404, detail="Content ID not found")
            
        return {"contentId": record.content_id, "status": record.status}
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=404, detail="Invalid ID format or not found")
