"""
Resume Parser Module
Handles extraction of text from various resume formats
"""

import os
from pathlib import Path
from typing import Optional


class ResumeParser:
    """Parse resume from various formats (text, PDF)"""
    
    SUPPORTED_FORMATS = {".txt", ".pdf", ".md"}
    
    @staticmethod
    def parse(file_path: str) -> str:
        """
        Parse resume from file or return raw text
        
        Args:
            file_path: Path to resume file or raw text
            
        Returns:
            Extracted resume text
            
        Raises:
            ValueError: If format not supported or parsing fails
        """
        # Check if it's a file path
        if os.path.isfile(file_path):
            return ResumeParser._parse_file(file_path)
        
        # Assume it's raw text
        if len(file_path) > 50:  # Likely raw text if long enough
            return file_path.strip()
        
        raise ValueError(f"Invalid resume input: {file_path}")
    
    @staticmethod
    def _parse_file(file_path: str) -> str:
        """Parse resume from file"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Resume file not found: {file_path}")
        
        file_ext = path.suffix.lower()
        
        if file_ext == ".txt" or file_ext == ".md":
            return ResumeParser._parse_text(file_path)
        elif file_ext == ".pdf":
            return ResumeParser._parse_pdf(file_path)
        else:
            raise ValueError(f"Unsupported resume format: {file_ext}")
    
    @staticmethod
    def _parse_text(file_path: str) -> str:
        """Parse plain text resume"""
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    
    @staticmethod
    def _parse_pdf(file_path: str) -> str:
        """Parse PDF resume"""
        try:
            from pypdf import PdfReader
        except ImportError:
            raise ImportError("pypdf required for PDF parsing. Install with: pip install pypdf")
        
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        
        return text.strip()
    
    @staticmethod
    def validate(resume_text: str, max_length: int = 10000) -> bool:
        """Validate resume text"""
        if not resume_text or not resume_text.strip():
            raise ValueError("Resume text is empty")
        
        if len(resume_text) > max_length:
            raise ValueError(f"Resume exceeds maximum length of {max_length} characters")
        
        return True
