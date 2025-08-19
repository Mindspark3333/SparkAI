from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database.base import Base


class ResearchResult(Base):
    __tablename__ = "research_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Original source info
    source_url = Column(String(2048), nullable=False)
    source_type = Column(String(100), nullable=False)  # e.g., 'pdf', 'web', 'video'
    title = Column(String(512), nullable=True)
    author = Column(String(256), nullable=True)
    published_at = Column(DateTime, nullable=True)

    # Extracted content
    raw_text = Column(Text, nullable=True)
    content_summary = Column(Text, nullable=True)
    key_points = Column(JSON, nullable=True)  # list of strings
    tags = Column(JSON, nullable=True)        # list of strings

    # AI analysis
    sentiment = Column(String(50), nullable=True)  # e.g., 'positive', 'neutral', 'negative'
    importance_score = Column(Integer, nullable=True)  # 1-100
    category = Column(String(100), nullable=True)      # e.g., 'economics', 'healthcare'

    # File storage references (if any)
    storage_key = Column(String(512), nullable=True)  # e.g., GCS object path
    metadata = Column(JSON, nullable=True)            # any extra info we want to store

    # Auditing
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="research_results")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "source_url": self.source_url,
            "source_type": self.source_type,
            "title": self.title,
            "author": self.author,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "raw_text": self.raw_text,
            "content_summary": self.content_summary,
            "key_points": self.key_points,
            "tags": self.tags,
            "sentiment": self.sentiment,
            "importance_score": self.importance_score,
            "category": self.category,
            "storage_key": self.storage_key,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }