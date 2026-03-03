from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from app.models.base import Base


class Issue(Base):
    __tablename__ = "issues"
    
    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False)
    
    title = Column(String(100), nullable=False)
    category = Column(String(50), default="其他")
    severity = Column(String(20), default="一般")
    status = Column(String(20), default="处理中")
    
    description = Column(Text, default="")
    landlord_response = Column(Text, default="")
    resolution = Column(Text, default="")
    
    reported_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    
    evidence_ids = Column(String(200), default="")  # comma-separated evidence ids
