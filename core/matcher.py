"""
Matcher Module
Core matching logic using Google Gemini AI
"""

import json
import re
from typing import Dict, Any, List, Tuple
import google.generativeai as genai

from config import Config
from core.resume_parser import ResumeParser
from core.jd_parser import JDParser


class Matcher:
    """AI-powered resume-JD matcher using Google Gemini"""
    
    def __init__(self, api_key: str = ""):
        """Initialize matcher with Google Gemini API"""
        api_key = api_key or Config.GOOGLE_API_KEY
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not set. Set it in environment or pass as argument.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(Config.LLM_MODEL)
        self.conversation_history = []
    
    def match(
        self,
        resume_text: str,
        jd_text: str,
        include_recommendations: bool = True,
    ) -> Dict[str, Any]:
        """
        Score and analyze resume against job description
        
        Args:
            resume_text: Resume text or file path
            jd_text: Job description text or file path
            include_recommendations: Whether to generate improvement recommendations
            
        Returns:
            Dictionary with score, explanation, and optionally recommendations
        """
        # Parse inputs
        resume_text = ResumeParser.parse(resume_text)
        ResumeParser.validate(resume_text)
        
        jd_text = JDParser.parse(jd_text)["raw_text"]
        JDParser.validate(jd_text)
        
        # Get score and explanation
        score, explanation = self._score(resume_text, jd_text)
        
        result = {
            "score": score,
            "explanation": explanation,
            "resume_preview": resume_text[:200] + "..." if len(resume_text) > 200 else resume_text,
            "jd_preview": jd_text[:200] + "..." if len(jd_text) > 200 else jd_text,
        }
        
        # Get recommendations if requested
        if include_recommendations:
            recommendations = self._recommend(resume_text, jd_text, score)
            result["recommendations"] = recommendations
        
        return result
    
    def _score(self, resume_text: str, jd_text: str) -> Tuple[float, str]:
        """
        Score resume against job description using Google Gemini
        
        Returns:
            Tuple of (score, explanation)
        """
        prompt = f"""You are an expert recruiter and career advisor. Analyze the following resume against the job description and provide a match score and explanation.

RESUME:
{resume_text}

JOB DESCRIPTION:
{jd_text}

Provide your analysis in JSON format with exactly these fields:
- score: A number from 0 to 100 representing the match quality
- explanation: A 2-3 sentence explanation of the score
- key_matches: List of 2-3 key skills/experiences that match well
- key_gaps: List of 2-3 critical missing skills/experiences

Focus on:
1. Technical skills alignment
2. Experience level match
3. Domain expertise
4. Cultural/role fit indicators

Respond ONLY with valid JSON, no other text."""

        response = self.model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                top_p=0.95,
            ),
        )
        
        response_text = response.text.strip()
        
        # Parse JSON response
        try:
            # Find JSON in response (in case there's extra text)
            json_match = re.search(r'\{[^{}]*\}', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(0)
            
            data = json.loads(response_text)
            score = float(data.get("score", 50))
            explanation = data.get("explanation", "Unable to generate explanation")
            
            # Ensure score is in valid range
            score = max(0, min(100, score))
            
            return score, explanation
        except json.JSONDecodeError:
            # Fallback: extract score if JSON parsing fails
            score_match = re.search(r'score["\']?\s*:\s*(\d+)', response_text, re.IGNORECASE)
            score = float(score_match.group(1)) if score_match else 50
            return score, "Analysis completed (parsing note: response format adjusted)"
    
    def _recommend(self, resume_text: str, jd_text: str, current_score: float) -> List[str]:
        """
        Generate recommendations to improve resume match
        
        Returns:
            List of recommendation strings
        """
        prompt = f"""You are an expert career coach. Given the resume, job description, and current match score of {current_score}/100, provide 3-5 specific, actionable recommendations to improve the match.

RESUME:
{resume_text[:2000]}

JOB DESCRIPTION:
{jd_text[:2000]}

Provide recommendations as a JSON array of strings. Each recommendation should be:
- Specific and actionable
- Ranked by impact (highest impact first)
- Realistic to implement

Format: {{"recommendations": ["rec1", "rec2", ...]}}

Respond ONLY with valid JSON."""

        response = self.model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                top_p=0.95,
            ),
        )
        
        response_text = response.text.strip()
        
        try:
            # Find JSON in response
            json_match = re.search(r'\{[^{}]*\}', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(0)
            
            data = json.loads(response_text)
            return data.get("recommendations", [])
        except (json.JSONDecodeError, KeyError):
            return ["Review job description carefully and highlight matching experiences"]
    
    def reset_history(self):
        """Reset conversation history"""
        self.conversation_history = []
