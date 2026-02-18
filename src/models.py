import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from src.database import Base

class Content(Base):
    __tablename__ = "content"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False, index=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ModerationResult(Base):
    __tablename__ = "moderation_results"
    content_id = Column(UUID(as_uuid=True), ForeignKey("content.id"), primary_key=True)
    status = Column(String, default="PENDING") # PENDING, APPROVED, REJECTED
    moderated_at = Column(DateTime, nullable=True)
