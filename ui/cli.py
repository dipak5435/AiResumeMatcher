"""
Command-Line Interface
Main entry point for CLI usage
"""

import argparse
import sys
import json
from typing import Optional

from core.matcher import Matcher
from core.database import Database
from core.resume_parser import ResumeParser
from core.jd_parser import JDParser


def print_match_result(result: dict, verbose: bool = False):
    """Pretty print match result"""
    print("\n" + "=" * 60)
    print(f"MATCH SCORE: {result['score']:.1f}/100")
    print("=" * 60)
    print(f"\nExplanation:\n{result['explanation']}")
    
    if "recommendations" in result and result["recommendations"]:
        print("\nRecommendations to Improve Match:")
        for i, rec in enumerate(result["recommendations"], 1):
            print(f"{i}. {rec}")
    
    if verbose:
        print(f"\nResume Preview: {result.get('resume_preview', 'N/A')[:100]}...")
        print(f"JD Preview: {result.get('jd_preview', 'N/A')[:100]}...")
    
    print("\n")


def cmd_match(args):
    """Handle match command"""
    try:
        # Validate inputs
        if not args.resume:
            print("Error: --resume is required")
            return False
        
        if not args.jd:
            print("Error: --jd is required")
            return False
        
        # Parse resume and JD
        print("Loading resume and job description...")
        try:
            resume_text = ResumeParser.parse(args.resume)
            ResumeParser.validate(resume_text)
        except Exception as e:
            print(f"Error parsing resume: {e}")
            return False
        
        try:
            jd_data = JDParser.parse(args.jd)
            jd_text = jd_data["raw_text"]
        except Exception as e:
            print(f"Error parsing job description: {e}")
            return False
        
        # Perform matching
        print("Analyzing with AI...")
        matcher = Matcher()
        result = matcher.match(resume_text, jd_text, include_recommendations=not args.no_recommendations)
        
        # Print result
        print_match_result(result, verbose=args.verbose)
        
        # Save to database if requested
        if args.save:
            db = Database()
            record = db.save_match(
                resume_text=resume_text,
                jd_text=jd_text,
                score=result["score"],
                explanation=result["explanation"],
                recommendations=result.get("recommendations", []),
            )
            print(f"✓ Match saved with ID: {record.id}")
        
        return True
    
    except Exception as e:
        print(f"Error: {e}")
        return False


def cmd_list_scores(args):
    """List all stored matches"""
    try:
        db = Database()
        stats = db.get_stats()
        
        print("\n" + "=" * 60)
        print("STORED MATCHES")
        print("=" * 60)
        
        if stats["total"] == 0:
            print("No matches stored yet. Use --save flag to persist matches.")
            return True
        
        print(f"Total matches: {stats['total']}")
        print(f"Average score: {stats['average_score']:.1f}/100")
        print("\nMatches (ordered by score):")
        print("-" * 60)
        
        matches = db.list_matches(limit=100, order_by="score")
        for i, match in enumerate(matches, 1):
            timestamp = match.timestamp.strftime("%Y-%m-%d %H:%M")
            print(f"{i}. ID: {match.id} | Score: {match.score:.1f} | {timestamp}")
            print(f"   {match.explanation[:80]}...")
        
        print("\n")
        return True
    
    except Exception as e:
        print(f"Error: {e}")
        return False


def cmd_recommend(args):
    """Get recommendations for improving a stored match"""
    try:
        if not args.score_id:
            print("Error: --score-id is required")
            return False
        
        db = Database()
        match = db.get_match(args.score_id)
        
        if not match:
            print(f"Error: Match with ID {args.score_id} not found")
            return False
        
        print("\n" + "=" * 60)
        print(f"RECOMMENDATIONS FOR MATCH ID: {match.id}")
        print("=" * 60)
        print(f"Current Score: {match.score:.1f}/100")
        print("\nRecommendations:")
        
        if match.recommendations:
            try:
                recs = json.loads(match.recommendations)
                for i, rec in enumerate(recs, 1):
                    print(f"{i}. {rec}")
            except:
                print(match.recommendations)
        else:
            print("No recommendations available for this match")
        
        print("\n")
        return True
    
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="AI-Powered Resume & JD Matcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --resume resume.pdf --jd "job_desc.txt" --save
  python main.py --list-scores
  python main.py --recommend --score-id 1
        """,
    )
    
    parser.add_argument("--resume", help="Path to resume file (PDF/TXT) or raw text")
    parser.add_argument("--jd", help="Path to job description file or raw text")
    parser.add_argument("--save", action="store_true", help="Save match to database")
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    parser.add_argument("--no-recommendations", action="store_true", help="Skip recommendations")
    parser.add_argument("--list-scores", action="store_true", help="List all stored matches")
    parser.add_argument("--recommend", action="store_true", help="Get recommendations for a match")
    parser.add_argument("--score-id", type=int, help="ID of match to get recommendations for")
    
    args = parser.parse_args()
    
    # Route to appropriate command
    if args.list_scores:
        success = cmd_list_scores(args)
    elif args.recommend:
        success = cmd_recommend(args)
    elif args.resume and args.jd:
        success = cmd_match(args)
    else:
        parser.print_help()
        return 1
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
