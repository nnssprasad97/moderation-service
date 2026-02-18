# Pydantic schemas for request/response validation and data serialization
from pydantic import BaseModel, UUID4, Field

# Request schema for content submission endpoint
class ContentSubmitRequest(BaseModel):
    userId: str = Field(..., min_length=1)
    text: str = Field(..., min_length=1)

# Response schema after successful submission
class ContentResponse(BaseModel):
    contentId: UUID4

# Response schema for status check with moderation decision
class StatusResponse(BaseModel):
    contentId: UUID4
    status: str
