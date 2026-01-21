"""
Unit tests for core modules
"""

import pytest
from core.resume_parser import ResumeParser
from core.jd_parser import JDParser
from core.database import Database
import tempfile
import os


class TestResumeParser:
    
    def test_parse_text_resume(self):
        """Test parsing plain text resume"""
        text = "John Doe\nSoftware Engineer\n5+ years experience"
        result = ResumeParser.parse(text)
        assert "John Doe" in result
        assert "Software Engineer" in result
    
    def test_validate_empty_resume(self):
        """Test validation of empty resume"""
        with pytest.raises(ValueError):
            ResumeParser.validate("")
    
    def test_validate_oversized_resume(self):
        """Test validation of oversized resume"""
        large_text = "x" * 20000
        with pytest.raises(ValueError):
            ResumeParser.validate(large_text)


class TestJDParser:
    
    def test_parse_jd(self):
        """Test parsing job description"""
        jd = "Senior Engineer. Requirements: 5+ years Python, AWS experience"
        result = JDParser.parse(jd)
        assert result["raw_text"] == jd
        assert result["length"] == len(jd)
    
    def test_validate_empty_jd(self):
        """Test validation of empty JD"""
        with pytest.raises(ValueError):
            JDParser.validate("")
    
    def test_extract_key_sections(self):
        """Test extraction of key sections"""
        jd = "About: Senior role. Requirements: Python, AWS. Nice to have: React"
        sections = JDParser.extract_key_sections(jd)
        assert "requirements" in sections or "nice_to_have" in sections


class TestDatabase:
    
    def test_save_and_retrieve_match(self):
        """Test saving and retrieving a match"""
        # Use in-memory SQLite for testing
        db = Database("sqlite:///:memory:")
        
        record = db.save_match(
            resume_text="Sample resume",
            jd_text="Sample JD",
            score=85.5,
            explanation="Good fit",
            recommendations=["Rec 1", "Rec 2"],
        )
        
        assert record.id is not None
        assert record.score == 85.5
        
        retrieved = db.get_match(record.id)
        assert retrieved.score == 85.5
    
    def test_list_matches(self):
        """Test listing matches"""
        db = Database("sqlite:///:memory:")
        
        db.save_match("resume1", "jd1", 80, "Good")
        db.save_match("resume2", "jd2", 90, "Excellent")
        
        matches = db.list_matches()
        assert len(matches) == 2
        assert matches[0].score == 90  # Should be ordered by score desc
    
    def test_get_stats(self):
        """Test stats generation"""
        db = Database("sqlite:///:memory:")
        
        db.save_match("resume1", "jd1", 70, "Good")
        db.save_match("resume2", "jd2", 90, "Excellent")
        
        stats = db.get_stats()
        assert stats["total"] == 2
        assert stats["average_score"] == 80.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
