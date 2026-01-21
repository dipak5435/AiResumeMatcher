"""
Database Module
Handles persistence of resume-JD matches and scores
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import json

from config import Config

Base = declarative_base()


class MatchRecord(Base):
    """Database model for resume-JD matches"""
    
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True)
    resume_text = Column(String, nullable=False)
    jd_text = Column(String, nullable=False)
    score = Column(Float, nullable=False)
    explanation = Column(String, nullable=False)
    recommendations = Column(String, nullable=True)  # JSON string
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert record to dictionary"""
        return {
            "id": self.id,
            "score": self.score,
            "explanation": self.explanation,
            "recommendations": json.loads(self.recommendations) if self.recommendations else [],
            "timestamp": self.timestamp.isoformat(),
        }


class Database:
    """Database manager for persistence"""
    
    def __init__(self, db_url: Optional[str] = None):
        """Initialize database connection"""
        db_url = db_url or Config.DATABASE_URL
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def save_match(
        self,
        resume_text: str,
        jd_text: str,
        score: float,
        explanation: str,
        recommendations: Optional[List[str]] = None,
    ) -> MatchRecord:
        """Save a resume-JD match to database"""
        session = self.SessionLocal()
        try:
            record = MatchRecord(
                resume_text=resume_text,
                jd_text=jd_text,
                score=score,
                explanation=explanation,
                recommendations=json.dumps(recommendations or []),
                timestamp=datetime.utcnow(),
            )
            session.add(record)
            session.commit()
            session.refresh(record)
            return record
        finally:
            session.close()
    
    def get_match(self, match_id: int) -> Optional[MatchRecord]:
        """Retrieve a specific match by ID"""
        session = self.SessionLocal()
        try:
            return session.query(MatchRecord).filter(MatchRecord.id == match_id).first()
        finally:
            session.close()
    
    def list_matches(self, limit: int = 100, order_by: str = "score") -> List[MatchRecord]:
        """List all matches, optionally ordered"""
        session = self.SessionLocal()
        try:
            query = session.query(MatchRecord)
            
            if order_by == "score":
                query = query.order_by(MatchRecord.score.desc())
            elif order_by == "recent":
                query = query.order_by(MatchRecord.timestamp.desc())
            
            return query.limit(limit).all()
        finally:
            session.close()
    
    def delete_match(self, match_id: int) -> bool:
        """Delete a match by ID"""
        session = self.SessionLocal()
        try:
            record = session.query(MatchRecord).filter(MatchRecord.id == match_id).first()
            if record:
                session.delete(record)
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about stored matches"""
        session = self.SessionLocal()
        try:
            count = session.query(MatchRecord).count()
            if count == 0:
                return {"total": 0, "average_score": 0}
            
            from sqlalchemy import func
            avg_score = session.query(func.avg(MatchRecord.score)).scalar() or 0
            
            return {
                "total": count,
                "average_score": round(avg_score, 1),
            }
        finally:
            session.close()
