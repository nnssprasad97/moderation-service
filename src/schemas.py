from pydantic import BaseModel, UUID4, Field

class ContentSubmitRequest(BaseModel):
    userId: str = Field(..., min_length=1)
    text: str = Field(..., min_length=1)

class ContentResponse(BaseModel):
    contentId: UUID4

class StatusResponse(BaseModel):
    contentId: UUID4
    status: str
