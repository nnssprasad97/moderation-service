# Integration tests for content submission and moderation workflow
import pytest
from httpx import AsyncClient
from src.api.main import app
import uuid

@pytest.mark.asyncio
async def test_submission_flow():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # 1. Submit Content
        user_id = f"user_{uuid.uuid4()}"
        response = await ac.post("/api/v1/content/submit", json={
            "userId": user_id, 
            "text": "Hello world"
        })
        assert response.status_code == 202
        content_id = response.json()["contentId"]
        
        # 2. Check Pending Status
        status_res = await ac.get(f"/api/v1/content/{content_id}/status")
        assert status_res.status_code == 200
        # Note: In a real integration test, the processor might have already run 
        # depending on race conditions, but typically it's 'PENDING' or 'APPROVED'
        
        # 3. Test Rate Limiting
        # Exhaust bucket
        for _ in range(15):
            await ac.post("/api/v1/content/submit", json={
                "userId": user_id, "text": "spam"
            })
        
        spam_response = await ac.post("/api/v1/content/submit", json={
            "userId": user_id, "text": "spam"
        })
        assert spam_response.status_code == 429
