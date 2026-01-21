# ARCHITECTURE & TECHNICAL DECISIONS

## System Overview

This AI-Powered Resume & JD Matcher evaluates candidate resumes against job descriptions using Google Gemini 2.5 Flash (free API), providing match scores (0-100), detailed justifications, and actionable improvement recommendations.

## System Architecture

### Three-Tier Architecture

```
┌─────────────────────────────────────────────────────┐
│              PRESENTATION LAYER (UI)                │
│  ┌──────────────────────────────────────────────┐   │
│  │  CLI Interface (cli.py)                      │   │
│  │  ├─ --resume: Analyze with recommendations  │   │
│  │  ├─ --list-scores: View all matches         │   │
│  │  └─ --recommend: Get improvement tips       │   │
│  └──────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────┐   │
│  │  Web Interface (web_app.py)                  │   │
│  │  ├─ Upload resume (PDF/TXT)                 │   │
│  │  ├─ Paste job description                   │   │
│  │  ├─ View results with recommendations       │   │
│  │  └─ See rankings of all matches             │   │
│  └──────────────────────────────────────────────┘   │
└──────────────────┬───────────────────────────────────┘
                   │ JSON API Calls
┌──────────────────▼───────────────────────────────────┐
│           BUSINESS LOGIC LAYER                       │
│  ┌──────────────────────────────────────────────┐   │
│  │  Matcher (matcher.py)                        │   │
│  │  ├─ Stage 1: Generate score & explanation   │   │
│  │  ├─ Stage 2: Generate recommendations       │   │
│  │  ├─ Google Gemini API integration           │   │
│  │  └─ Error handling & fallbacks              │   │
│  └──────────────────────────────────────────────┘   │
└──────────────────┬───────────────────────────────────┘
                   │ Data Processing
┌──────────────────▼───────────────────────────────────┐
│             DATA LAYER                               │
│  ┌──────────────────────────────────────────────┐   │
│  │  Resume Parser (resume_parser.py)            │   │
│  │  ├─ PDF extraction (pypdf)                   │   │
│  │  ├─ Text file parsing                        │   │
│  │  └─ Input validation                         │   │
│  └──────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────┐   │
│  │  JD Parser (jd_parser.py)                    │   │
│  │  ├─ Text extraction                          │   │
│  │  ├─ Section identification                   │   │
│  │  └─ Validation                               │   │
│  └──────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────┐   │
│  │  Database (database.py)                      │   │
│  │  ├─ SQLAlchemy ORM                           │   │
│  │  ├─ SQLite persistence                       │   │
│  │  └─ Query & statistics                       │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### Modular Design

```
resume_matcher/
├── core/
│   ├── resume_parser.py      # Text extraction (PDF/TXT support)
│   ├── jd_parser.py          # Job description parsing
│   ├── matcher.py            # AI scoring engine using Google Gemini
│   └── database.py           # SQLAlchemy persistence layer
├── ui/
│   ├── cli.py                # Command-line interface
│   ├── web_app.py            # Flask REST API
│   └── static/templates/     # HTML/CSS/JS frontend
├── main.py                   # Entry point (CLI/Web routing)
└── config.py                 # Configuration management
```

### Core Components

**1. Resume Parser (`core/resume_parser.py`)**
- Supports PDF (pypdf), plain text, and Markdown
- Validates resume length constraints (max 10KB)
- Handles file path or raw text input

**2. JD Parser (`core/jd_parser.py`)**
- Parses job descriptions and validates length (max 5KB)
- Extracts key sections (requirements, nice-to-have) via pattern matching
- Provides structured data for AI analysis

**3. Matcher (`core/matcher.py`)**
- Core AI logic using Google Gemini 2.5 Flash API
- Two-stage scoring process:
  - **Stage 1**: Score & Justification (JSON-formatted)
  - **Stage 2**: Recommendations (generated separately for clarity)
- Uses structured prompts to ensure consistent JSON responses
- Implements error handling with fallbacks

### Data Flow Walkthrough

```
1. USER INPUT
   ├─ Resume file (PDF/TXT/MD)
   └─ Job description text

2. PARSING STAGE
   ├─ resume_parser.parse() → Extract text from file
   ├─ jd_parser.parse() → Extract text from input
   └─ Validation → Check file size, text length

3. MATCHING STAGE (Two-Stage AI Prompting)
   │
   ├─ STAGE 1: Scoring
   │  ├─ Construct prompt with resume + JD
   │  ├─ Call Gemini 2.5 Flash API
   │  ├─ Parse JSON response
   │  └─ Extract: score (0-100) + explanation
   │
   └─ STAGE 2: Recommendations
      ├─ Construct recommendation prompt
      ├─ Call Gemini 2.5 Flash API
      ├─ Parse JSON response
      └─ Extract: actionable recommendations array

4. DATABASE PERSISTENCE
   ├─ Create MatchRecord instance
   ├─ Store: resume_text, jd_text, score, explanation, recommendations
   └─ SQLite database (matches.db)

5. RESPONSE TO USER
   ├─ CLI: Print score + explanation + recommendations
   ├─ Web API: Return JSON response with all fields
   └─ Dashboard: Display ranking, history, statistics
```

### REST API Endpoints

| Method | Endpoint | Purpose | Request | Response |
|--------|----------|---------|---------|----------|
| POST | `/api/match` | Score resume against JD | `{resume_text, jd_text}` | `{score, explanation, recommendations}` |
| GET | `/api/matches` | List all matches | Query: `sort`, `limit` | Array of match records |
| GET | `/api/match/<id>` | Get specific match | URL: `id` | Single match record |
| DELETE | `/api/match/<id>` | Delete match | URL: `id` | `{success: true}` |
| GET | `/api/stats` | Get statistics | — | `{total_matches, avg_score}` |
| POST | `/api/upload-resume` | Upload resume file | FormData: `file` | `{resume_text, filename}` |

### Component Interactions

**Resume Parser → Matcher**
```
ResumeParser.parse(file_path) 
  → Detects format (PDF/TXT/MD)
  → Extracts text content
  → Returns structured resume text to Matcher
```

**JD Parser → Matcher**
```
JdParser.parse(text)
  → Validates length constraints
  → Extracts key sections
  → Returns cleaned JD text to Matcher
```

**Matcher → Google Gemini API**
```python
# Stage 1: Generate score + explanation
score_response = model.generate_content(scoring_prompt)
score_data = json.loads(score_response.text)

# Stage 2: Generate recommendations
rec_response = model.generate_content(recommendation_prompt)
recommendations = json.loads(rec_response.text)['recommendations']
```

**Matcher → Database**
```python
db.save_match(
    resume_text=resume,
    jd_text=jd,
    score=score,
    explanation=explanation,
    recommendations=recommendations
)
```

### Technology Stack Rationale

| Component | Technology | Justification |
|-----------|-----------|---------------|
| **Language** | Python 3.9+ | Rich ecosystem (pypdf, SQLAlchemy), rapid development |
| **Web Framework** | Flask | Lightweight, minimal overhead, perfect for REST APIs |
| **AI Model** | Google Gemini 2.5 Flash | Free API tier, no cost constraints, consistent JSON outputs |
| **Database** | SQLite + SQLAlchemy | Development simplicity, easy migration to PostgreSQL |
| **PDF Parsing** | pypdf | Pure Python implementation, reliable text extraction |
| **Frontend** | Vanilla JS + CSS3 | No build process required, responsive design |
| **Config Management** | python-dotenv | Environment-based secrets, no hardcoded credentials |

### Performance Characteristics

| Operation | Duration | Bottleneck |
|-----------|----------|-----------|
| Resume PDF parsing | 0.5-2s | File size, pypdf extraction speed |
| JD text parsing | <100ms | Input validation only |
| Gemini API call | 2-5s | Network latency + model inference |
| Database save | <100ms | SQLite disk I/O |
| **Total per match** | **3-7s** | External Gemini API |

### Scalability Path

**Current (MVP)**
```
- Single-threaded execution
- SQLite file-based database
- Free Gemini API tier
- Maximum: ~5-10 requests/minute
```

**Phase 2: Growth**
```
- Async job queue (Celery + Redis)
- PostgreSQL for concurrent users
- Implemented rate limiting
- Maximum: 100+ requests/minute
```

**Phase 3: Enterprise**
```
- Kubernetes containerization
- Database sharding/replication
- Model fine-tuning on company data
- Batch processing pipeline
- Maximum: 1000+ requests/minute
```

### Deployment Architecture

**Development Environment**
```bash
# CLI mode
python main.py --resume samples/sample_resume.txt --jd samples/sample_jd.txt

# Web mode
python main.py --web  # Runs on http://127.0.0.1:5000
```

**Production Deployment**
```yaml
Web Server:
  - Gunicorn (WSGI application server)
  - Nginx (reverse proxy + load balancer)
  - Flask (REST API)
  
Database:
  - PostgreSQL (replaces SQLite)
  - Connection pooling (SQLAlchemy)
  
Containerization:
  - Docker (application image)
  - Docker Compose (local development)
  
Monitoring:
  - Application logs
  - Error tracking (Sentry)
  - Performance metrics
```

### Error Handling Strategy

```python
# Layered error handling approach:

1. Input Validation
   └─ Invalid file format → User-friendly error message
   └─ File too large → Suggest file compression
   
2. API Calls
   └─ Timeout → Retry with exponential backoff
   └─ Rate limit → Queue request for later
   └─ Invalid response → Parse fallback format
   
3. Database Operations
   └─ Connection error → Log and notify
   └─ Transaction failure → Rollback changes
   
4. UI Responses
   └─ Always return meaningful error messages
   └─ Log full errors server-side for debugging
```

**4. Database (`core/database.py`)**
- SQLAlchemy ORM with SQLite backend
- Stores: resume text, JD text, score, explanation, recommendations
- Query capabilities: sort by score/recency, pagination
- Statistics: total count, average score

### UI Layer

**CLI (`ui/cli.py`)**
- Commands: `--match`, `--list-scores`, `--recommend`
- Example: `python main.py --resume resume.pdf --jd jd.txt --save`
- Supports file upload and raw text input

**Web UI (`ui/web_app.py`)**
- Flask REST API with Jinja2 templating
- Endpoints:
  - POST `/api/match` - Perform matching
  - GET `/api/matches` - List with pagination
  - GET/DELETE `/api/match/{id}` - Individual match operations
  - POST `/api/upload-resume` - PDF/TXT file upload

**Frontend (`ui/static/`)**
- Responsive HTML5/CSS3 interface
- Vanilla JavaScript for API interaction
- Real-time score visualization
- Match history with rankings

## AI Strategy

### Why Google Gemini 2.5 Flash?

1. **Reasoning Capability**: Superior at understanding context between resume and job requirements
2. **JSON Mode**: Reliable structured output for programmatic parsing
3. **Cost-Effective**: Sonnet provides excellent performance/cost ratio for this task
4. **Instruction Following**: Precise response formatting for integration

### Prompt Engineering

**Scoring Prompt**:
- Provides both resume and JD in clear sections
- Instructs model to focus on: technical skills, experience level, domain expertise, cultural fit
- Requests JSON output with: score (0-100), explanation (2-3 sentences), key matches/gaps
- Includes fallback parsing for malformed responses

**Recommendation Prompt**:
- Separated from scoring to allow focused improvement suggestions
- Prioritized by impact (highest first)
- Ensures recommendations are actionable and realistic

### Example Prompt Structure
```
You are an expert recruiter. Analyze this resume against the job description.

RESUME:
[resume text]

JOB DESCRIPTION:
[jd text]

Provide analysis in JSON:
{
  "score": 0-100,
  "explanation": "2-3 sentences",
  "key_matches": ["skill1", "skill2"],
  "key_gaps": ["skill3", "skill4"]
}

Focus on: technical skills alignment, experience match, domain expertise.
Respond ONLY with valid JSON.
```

## Data Flow

1. **User Input** → Resume + JD (file or text)
2. **Parsing** → Extract and validate text
3. **AI Analysis** → Gemini 2.5 Flash scores and generates explanation
4. **Recommendations** → Gemini 2.5 Flash generates improvement suggestions
5. **Persistence** → Optional database save
6. **Output** → Score, explanation, recommendations to user

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| Gemini API over embeddings | Needs reasoning about context, not just similarity |
| SQLite over cloud DB | MVP simplicity; can migrate to PostgreSQL later |
| Flask over FastAPI | Simpler async handling for this use case |
| Vanilla JS frontend | No external dependencies; maintainable for small project |
| Modular structure | Each component independently testable and reusable |
| JSON response format | Reliable parsing, easier integration, clearer output |

## Scalability Considerations

- **Batch Processing**: Can add queue system (Celery) for bulk resume analysis
- **Caching**: LRU cache for identical resume-JD pairs (common in recruiting)
- **Database**: SQLite → PostgreSQL for concurrent access
- **API Rate Limiting**: Add rate limiting for Gemini API (per Google's quota limits)
- **Async Processing**: Upgrade to async Flask or use Gunicorn for concurrent requests

## Error Handling

- **API Failures**: Retry logic with exponential backoff
- **Parsing Failures**: Graceful fallbacks (generic scoring if JSON parse fails)
- **File Errors**: Clear error messages for unsupported formats
- **Validation**: Input length constraints prevent API overload

## Testing

- Unit tests for parsers, database operations
- Integration tests for full matching flow
- Manual CLI testing with sample files

## Future Enhancements

1. **RAG Integration**: Store job market data, skill requirements to improve context
2. **Fine-tuning**: Train Gemini on recruiting domain data via Google API
3. **Multi-model Support**: Add OpenAI GPT-4, Gemini for comparison
4. **Analytics Dashboard**: Visualize trends in skill gaps, match distribution
5. **Resume Optimization**: Real-time suggestions while user edits resume
6. **Batch Processing**: Bulk resume screening for recruiters
