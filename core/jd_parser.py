"""
Job Description Parser Module
Handles extraction and structuring of job descriptions
"""

from typing import Dict, List, Any


class JDParser:
    """Parse and extract structured information from job descriptions"""
    
    @staticmethod
    def parse(jd_text: str) -> Dict[str, Any]:
        """
        Parse raw job description text
        
        Args:
            jd_text: Raw job description text
            
        Returns:
            Structured job description data
        """
        JDParser.validate(jd_text)
        
        return {
            "raw_text": jd_text.strip(),
            "length": len(jd_text),
        }
    
    @staticmethod
    def validate(jd_text: str, max_length: int = 5000) -> bool:
        """Validate job description text"""
        if not jd_text or not jd_text.strip():
            raise ValueError("Job description text is empty")
        
        if len(jd_text) > max_length:
            raise ValueError(f"Job description exceeds maximum length of {max_length} characters")
        
        return True
    
    @staticmethod
    def extract_key_sections(jd_text: str) -> Dict[str, str]:
        """
        Try to identify key sections in job description
        (used for context in matching)
        """
        sections = {
            "about_role": JDParser._extract_section(jd_text, ["responsibility", "about", "overview"]),
            "requirements": JDParser._extract_section(jd_text, ["requirement", "requirement", "must have", "must-have"]),
            "nice_to_have": JDParser._extract_section(jd_text, ["nice to have", "preferred", "bonus", "desirable"]),
        }
        return {k: v for k, v in sections.items() if v}
    
    @staticmethod
    def _extract_section(text: str, keywords: List[str]) -> str:
        """Extract section based on keywords"""
        text_lower = text.lower()
        for keyword in keywords:
            idx = text_lower.find(keyword)
            if idx != -1:
                # Return text from keyword onwards, limited to reasonable length
                return text[idx:idx+1000]
        return ""
