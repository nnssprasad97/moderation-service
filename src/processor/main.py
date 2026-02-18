# Background processor worker - consumes events from Redis and performs moderation
import asyncio
import json
import redis.asyncio as redis
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from src.config import settings
from src.database import AsyncSessionLocal
from src.models import ModerationResult

async def process_content(session: AsyncSession, event_data: dict):
    content_id = event_data['contentId']
    text = event_data['text']
    
    print(f"Processing content: {content_id}")
    
    # Mock Moderation Logic
    # Reject if contains 'badword', otherwise Approve
    status = "REJECTED" if "badword" in text.lower() else "APPROVED"
    
    # Update DB
    stmt = (
        update(ModerationResult)
        .where(ModerationResult.content_id == content_id)
        .values(status=status, moderated_at=datetime.utcnow())
    )
    await session.execute(stmt)
    await session.commit()
    print(f"Content {content_id} marked as {status}")

async def main():
    print("Starting Moderation Processor...")
    r = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
    
    while True:
        try:
            # Blocking pop - waits for an item in the queue
            # Returns tuple: (queue_name, data)
            item = await r.blpop(settings.QUEUE_NAME, timeout=0) 
            if item:
                _, data = item
                event = json.loads(data)
                
                async with AsyncSessionLocal() as session:
                    await process_content(session, event)
                    
        except Exception as e:
            print(f"Error processing event: {e}")
            await asyncio.sleep(1) # Backoff on crash

if __name__ == "__main__":
    asyncio.run(main())
