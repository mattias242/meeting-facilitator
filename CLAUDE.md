# Meeting Facilitator AI

> AI-driven mötesassistent som aktivt deltar i fysiska möten genom att använda IDOARRT-ramverket och GROW-coachingmodellen för att facilitera och coacha grupper mot sina mål.

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Frontend     │────▶│     Backend     │────▶│    Database     │
│  React + TS     │◀────│   FastAPI       │     │    SQLite       │
│  Web Audio API  │  WS │   Claude API    │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

**Flow**: IDOARRT upload → Live meeting (audio recording → transcription → trigger analysis → facilitation questions) → Protocol generation

## Tech Stack

### Frontend
- **Framework**: React 18
- **Language**: TypeScript
- **Build**: Vite
- **Audio**: Web Audio API (MediaRecorder)
- **State**: React hooks
- **API**: Axios + WebSocket

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: SQLite + SQLAlchemy ORM (encrypted)
- **AI**: Claude Sonnet API (Anthropic)
- **Real-time**: WebSocket (authenticated)
- **Security**: JWT auth, field-level encryption
- **Testing**: pytest + TDD

## Project Structure

```
meeting-facilitator/
├── frontend/                       # React + TypeScript
│   ├── src/
│   │   ├── components/
│   │   │   ├── preparation/       # Fas 1: IDOARRT upload
│   │   │   ├── live-meeting/      # Fas 2: Live session
│   │   │   └── wrap-up/           # Fas 3: Protocol
│   │   ├── pages/
│   │   ├── hooks/                 # useWebSocket, useAudioRecorder, useMeeting
│   │   ├── services/              # api.ts, websocket.ts
│   │   └── types/
│   ├── package.json
│   └── tsconfig.json
├── backend/                        # FastAPI
│   ├── app/
│   │   ├── main.py                # FastAPI app + WebSocket endpoint
│   │   ├── models/                # SQLAlchemy models
│   │   ├── schemas/               # Pydantic schemas
│   │   ├── api/v1/                # REST endpoints
│   │   ├── services/
│   │   │   ├── idoarrt_service.py      # IDOARRT parser
│   │   │   ├── claude_service.py       # Claude API integration
│   │   │   ├── trigger_service.py      # Intervention triggers
│   │   │   ├── facilitation_service.py # Question generation
│   │   │   └── protocol_service.py     # Protocol generation
│   │   ├── core/
│   │   │   ├── websocket.py            # WebSocket manager
│   │   │   ├── auth.py                 # JWT authentication
│   │   │   ├── encryption.py          # Database encryption
│   │   │   └── file_security.py       # File upload security
│   │   └── db/
│   │       └── session.py
│   ├── tests/
│   ├── requirements.txt
│   └── pyproject.toml
├── docs/
│   ├── IDOARRT-format.md          # IDOARRT markdown template
│   ├── intervention-triggers.md   # Trigger logic documentation
│   ├── TDD-GUIDELINES.md          # Test-driven development guidelines
│   └── AUDIT.md                   # Security audit report
├── .claude/
│   └── commands/
│       ├── test-meeting-flow.md
│       └── test-claude-api.md
├── .github/
│   └── workflows/
│       └── test-suite.yml         # CI/CD pipeline
├── backend/.env.example           # Environment configuration
└── CLAUDE.md
```

## Commands

### Frontend
```bash
cd frontend
npm install           # First-time setup
npm run dev           # Start dev server (port 5173)
npm run build         # Build for production
npm run typecheck     # Check TypeScript
npm run lint          # ESLint
```

### Backend
```bash
cd backend
python -m venv venv                        # First-time setup
source venv/bin/activate                   # Activate virtual environment
pip install -r requirements.txt            # Install dependencies
uvicorn app.main:app --reload --port 8000  # Start API server
pytest                                      # Run tests
ruff check . && mypy app/                  # Lint + typecheck
```

### Environment Setup
```bash
# Backend
cp backend/.env.example backend/.env
# Add your ANTHROPIC_API_KEY to backend/.env
# Set JWT_SECRET_KEY and DB_ENCRYPTION_KEY for security

# Frontend
cp frontend/.env.example frontend/.env
```

## Development Workflow

### Git Workflow (Pure Trunk-Based Development)
```
main (trunk) ── Direct commits only
```

**Pure Trunk-Based Strategy**:
- **main**: All work happens directly in main
- **No branches**: No feature branches, no long-lived branches
- **Direct commits**: All changes go straight to main
- **Continuous integration**: Every commit tested immediately
- **Always production-ready**: Main is always deployable

### Normal Development
1. **Setup environment**: Configure `.env` files with security keys
2. **Work directly in main**: Stay on main branch always
3. **Start backend**: `cd backend && source venv/bin/activate && uvicorn app.main:app --reload`
4. **Start frontend**: `cd frontend && npm run dev`
5. **Access app**: http://localhost:5173
6. **API docs**: http://localhost:8000/docs
7. **Login**: Get JWT token via `/api/v1/auth/login`
8. **Test frequently**: Run TDD tests before commits
9. **Commit directly to main**: Small, frequent commits

### Testing Commands
```bash
# Backend
cd backend
pytest                          # Run all tests
pytest tests/test_services/      # Service tests only
pytest --cov=app                # With coverage

# Frontend  
cd frontend
npm test                         # Run all tests
npm run test:ui                 # Interactive UI
npm run test:coverage           # With coverage

# TDD Workflow
pytest tests/test_services/test_idoarrt_service.py::TestIDOARRTService::test_parse_valid_idoarrt_success -v
```

### Logging Commands
```bash
# Backend - View logs in real-time
cd backend
tail -f logs/app.log              # General application logs
tail -f logs/errors.log           # Error logs only
tail -f logs/api.log              # API request logs
tail -f logs/security.log         # Security events
tail -f logs/audio.log            # Audio processing logs

# Backend - Search logs
grep "ERROR" logs/app.log
grep "meeting_id" logs/api.log
grep "SECURITY_EVENT" logs/security.log

# Frontend - Access logs (browser console)
window.logger.getLogs()            # Recent logs in memory
window.logger.exportLogs()         # Download all logs
window.logger.clearLogs()           # Clear all logs
```

### Git Commands
```bash
# Always stay on main
git checkout main

# Commit directly to main
git add .
git commit -m "feat: Add feature with tests"

# Push to main
git push origin main

# No branch management needed
```

### Testing a Complete Meeting Flow
1. Upload IDOARRT markdown file
2. Start meeting
3. Record audio (browser will request microphone permission)
4. Observe transcriptions and interventions in real-time
5. End meeting
6. Review protocol

### Pure Trunk-Based Principles
- **Small commits**: Commit frequently with small changes
- **Test before commit**: Run tests to ensure main stays green
- **No branches**: All work in main branch
- **Continuous integration**: Every commit validated
- **Always deployable**: Main is always production-ready

### 📊 Logging Strategy
- **Local files first**: All logs stored locally in `logs/` directory
- **Multi-file separation**: Different log files for different concerns
- **Real-time monitoring**: Use `tail -f` for live log viewing
- **Frontend persistence**: Browser logs stored in localStorage
- **Future log service**: Planned integration with cloud logging services

### 📁 Current Log Files
```
backend/logs/
├── app.log          # General application logs
├── errors.log       # Error and exception logs
├── security.log     # Authentication events
├── api.log          # HTTP request/response logs
├── audio.log        # Audio processing events
└── claude.log       # Claude API interactions

# Frontend logs (localStorage + browser console)
- User actions and interactions
- API requests and responses
- Audio recording events
- WebSocket connections
- Error tracking
```

## Key Concepts

### IDOARRT Framework
All meetings are structured around:
- **I**ntent: Why we're meeting
- **D**esired **O**utcomes: What we want to achieve
- **A**genda: Topics with time allocations
- **R**oles: Who does what (facilitator, timekeeper, etc.)
- **R**ules: How we work together
- **T**ime: Total duration in minutes

### Intervention Types
The assistant can intervene with:
- **time_warning**: Triggered at 50%, 75%, and 5min remaining
- **goal_deviation**: When discussion strays from desired outcomes
- **perspective_gap**: When only 1-2 people are talking
- **complexity_mistake**: When treating simple issues as complex or vice versa

### Facilitation Question Types
Based on GROW coaching model:
- **Perspective-expanding**: "Vilka andra perspektiv finns? Vem påverkas som inte är här?"
- **Focus-keeping**: "Hur relaterar detta till vårt mål om X?"
- **Coaching (GROW)**: "Var är vi nu? Vad är våra alternativ? Vad gör vi härnäst?"

## Claude Integration Points

1. **Transcription**: Audio chunks (2-min) → Claude API → Text
2. **Trigger Analysis**: Transcription + IDOARRT context → Claude → Detect issues
3. **Question Generation**: Intervention type + context → Claude → Coaching question
4. **Protocol Generation**: Full transcription + IDOARRT → Claude → Structured summary

Note: If Claude doesn't support audio directly, use OpenAI Whisper API as fallback.

## Verification Checklist

### Before Committing Backend Changes
1. ✅ `ruff check .` passes
2. ✅ `mypy app/` passes
3. ✅ `pytest` passes
4. ✅ API endpoints tested manually or with tests
5. ✅ WebSocket events work correctly

### Before Committing Frontend Changes
1. ✅ `npm run typecheck` passes
2. ✅ `npm run lint` passes
3. ✅ Components render correctly
4. ✅ API integration works
5. ✅ WebSocket connection stable

### Full Integration Testing
1. ✅ Upload valid IDOARRT file
2. ✅ Start meeting and verify audio recording
3. ✅ Verify transcription appears after 2min
4. ✅ Test time-based interventions
5. ✅ Test manual meeting end
6. ✅ Verify protocol generation
7. ✅ Check database for saved records

## API Endpoints

```
POST   /api/v1/meetings                          # Upload IDOARRT, parse, validate
GET    /api/v1/meetings/{id}                     # Get meeting details
PATCH  /api/v1/meetings/{id}/start               # Start meeting
PATCH  /api/v1/meetings/{id}/extend              # Extend by 5 minutes
PATCH  /api/v1/meetings/{id}/end                 # End meeting
POST   /api/v1/meetings/{id}/audio-chunks        # Upload 2-minute audio chunk
GET    /api/v1/meetings/{id}/interventions       # Get all interventions
GET    /api/v1/meetings/{id}/protocol            # Get protocol
POST   /api/v1/meetings/{id}/protocol/generate   # Generate protocol
```

WebSocket endpoint: `ws://localhost:8000/ws/meetings/{meeting_id}`

## File Boundaries

- **Frontend safe**: `frontend/src/`
- **Backend safe**: `backend/app/`, `backend/tests/`
- **Config files**: Edit carefully, always test after changing
- **Never touch**: `*/node_modules/`, `*/__pycache__/`, `*.db`, `.git/`

## Common Tasks

### Add New Intervention Type
1. Add type to `backend/app/services/trigger_service.py`
2. Add prompt template in `backend/app/services/facilitation_service.py`
3. Update frontend `useWebSocket.ts` to handle new event
4. Update `AssistantOutput.tsx` to display new intervention

### Test Claude API Integration
```bash
cd backend
pytest tests/test_services/test_claude_service.py -v
```

### Debug WebSocket Events
Open browser console during live meeting to see real-time WebSocket traffic.

### Update Database Schema
```bash
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## Known Limitations

### Functional Limitations
1. **Single meeting at a time** - No concurrent meeting support
2. **Swedish language only** - Transcription and questions in Swedish
3. **No speaker diarization** - Can't identify who said what

### Security Limitations (CRITICAL)
4. **No active authentication** - All API endpoints are open (auth framework exists but disabled)
5. **No user system** - Login accepts any credentials
6. **Audio not encrypted** - Largest data asset stored in cleartext
7. **Hardcoded secrets** - Default JWT and encryption keys in source code
8. **No rate limiting** - Vulnerable to DoS and cost explosion
9. **Frontend lacks auth** - No token handling implemented
10. **Development only** - **NOT suitable for production or sensitive data**

**IMPORTANT**: Se [AUDIT.md](AUDIT.md) för fullständig lista av 12 kritiska och 8 medelhöga särbarheter.

## 🔒 Security Status

**IMPORTANT**: Systemet är INTE production-ready. Se [AUDIT.md](AUDIT.md) för fullständig säkerhetsanalys.

### ✅ Implemented & Active
- **File Upload Security**: MIME type validation, size limits, content scanning (`app/core/file_security.py`)
- **Input Validation**: Strict Pydantic schemas with security checks (`StrictMeetingCreate`, `StrictAudioChunkUpload`)
- **Partial Database Encryption**: Transcriptions och protocols encrypted (audio blobs ej encrypted)
- **TDD Framework**: Complete test infrastructure

### ⚠️ Implemented but DISABLED
- **JWT Authentication Framework**: Kod finns men **kommenterad ut** på alla endpoints
- **WebSocket Token Validation**: Kod finns men **bypassed för development**
- **User Authentication**: Login endpoint accepterar **vilka credentials som helst**

### 🚨 Critical Security Issues
**12 kritiska sårbarheter** identifierade i [AUDIT.md](AUDIT.md):
1. **Ingen aktiv authentication** - Alla endpoints öppna
2. **Audio blobs okrypterade** - Största data-asset i klartext
3. **Hardcoded secrets** - JWT secret och encryption key i källkod
4. **Ingen authorization** - User ownership checks saknas
5. **Ingen rate limiting** - DoS och cost explosion risk
6. **Frontend utan auth** - Inga auth headers implementerade

### 📋 Security Roadmap
- **Phase 1 (Vecka 1-2)**: Aktivera & fixa authentication, kryptera audio, fixa hardcoded secrets
- **Phase 2 (Vecka 3-4)**: Rate limiting, audit logging, error handling
- **Phase 3 (Vecka 5-8)**: Security headers, session management, data retention

**Fullständig analys**: Se [AUDIT.md](AUDIT.md) för detaljerad säkerhetsaudit och åtgärdsplan.

## Future Enhancements

- Multi-language support
- Speaker identification (ML-based diarization)
- Voice synthesis for assistant questions
- Remote/hybrid meeting support (online + physical)
- Calendar integration
- Analytics dashboard (meeting effectiveness over time)
- Production deployment with advanced security

## Troubleshooting

### Backend won't start
- Check Python version: `python --version` (must be 3.11+)
- Verify virtual environment: `which python` should point to `venv/bin/python`
- Check dependencies: `pip install -r requirements.txt`

### Frontend won't connect to backend
- Verify backend is running on port 8000
- Check CORS settings in `backend/app/main.py`
- Verify `.env` files exist in both frontend and backend

### Audio recording not working
- Browser must support MediaRecorder API (Chrome, Firefox, Edge)
- User must grant microphone permission
- Check browser console for errors

### Authentication Issues
- Verify JWT_SECRET_KEY is set in backend/.env
- Check token expiration (default 30 minutes)
- Use `/api/v1/auth/login` to get fresh token

### Claude API errors
- Verify `ANTHROPIC_API_KEY` in `backend/.env`
- Check API rate limits
- Review error messages in backend logs

## Development Tips

1. **Use API docs**: http://localhost:8000/docs for interactive API testing
2. **Monitor WebSocket**: Open browser DevTools → Network → WS to see WebSocket messages
3. **Check database**: Use SQLite browser to inspect `meeting_facilitator.db` (encrypted data)
4. **Test with short meetings**: Use 5-minute IDOARRT for faster testing
5. **Mock audio**: Consider creating test audio files for consistent testing
6. **Security testing**: Run `pytest tests/` to verify security measures
7. **TDD workflow**: Write tests first, then implement features

## 🚀 Next Steps & Roadmap

**Current Status**: Development/testing only - NOT production-ready

### Phase 0 Complete ✅ (Foundation)
- [x] Core application structure
- [x] IDOARRT parser and validation
- [x] Audio recording and transcription
- [x] WebSocket real-time communication
- [x] Input validation framework
- [x] File upload security
- [x] TDD framework established
- [x] Pure trunk-based development workflow
- [x] Logging infrastructure

### Phase 1 - Critical Security (NEXT - Vecka 1-2) 🚨
**Status**: BLOCKING för production deployment

- [ ] **Aktivera authentication på alla endpoints** (ta bort comments)
- [ ] **Implementera proper user authentication** (bcrypt password hashing)
- [ ] **Skapa user database model** med ownership
- [ ] **Lägg till authorization checks** (user owns resource)
- [ ] **Kryptera audio blobs** (property-based encryption)
- [ ] **Fixa hardcoded secrets** (kräv environment variables)
- [ ] **Aktivera WebSocket authentication** (ta bort dev bypass)
- [ ] **Implementera frontend auth** (login, token storage, headers)
- [ ] **Auth test coverage** > 95%

**Exit Criteria**:
- ✅ Alla endpoints kräver authentication
- ✅ All känslig data encrypted (audio + text)
- ✅ Inga hardcoded secrets i kod
- ✅ Security scan: 0 critical, 0 high vulnerabilities

### Phase 2 - Production Hardening (Vecka 3-4)
- [ ] Rate limiting implementation (FastAPI-Limiter)
- [ ] Audit logging för security events
- [ ] Error handling (generic messages i production)
- [ ] UUID validation för alla ID parameters
- [ ] Security headers (CSP, HSTS, X-Frame-Options)
- [ ] CORS tightening (explicit allow lists)

**Exit Criteria**:
- ✅ Rate limiting aktivt
- ✅ Audit logs för alla security events
- ✅ Error messages inte exponerar internals

### Phase 3 - Enterprise Features (Vecka 5-8)
- [ ] Session management (token revocation, logout)
- [ ] Data retention policy (auto-cleanup)
- [ ] Database file encryption (SQLCipher)
- [ ] Multi-language support
- [ ] Speaker diarization
- [ ] Log service integration (cloud logging)
- [ ] Penetration testing

**Exit Criteria**:
- ✅ GDPR compliance uppnådd
- ✅ Penetration test passed
- ✅ Production deployment guide complete

### Phase 4 - Advanced Features (Månad 3+)
- [ ] Voice synthesis for assistant questions
- [ ] Remote/hybrid meeting support
- [ ] Calendar integration
- [ ] Analytics dashboard
- [ ] Centralized log management
- [ ] Real-time log monitoring dashboard

### 🌲 Pure Trunk-Based Workflow
- **Main branch only**: All work happens in main
- **No feature branches**: Direct commits only
- **TDD integration**: Tests before every commit
- **Continuous integration**: Automated testing on every push
- **Always deployable**: Main is always production-ready

### 📋 Quality Gates
- All tests must pass before every commit
- Security scan must be clean
- Code coverage > 80%
- No critical vulnerabilities
- Pure trunk-based: No branches, direct commits only
- Log monitoring: Check logs for errors and performance issues

## 🔧 Monitoring & Debugging

### 📊 Local Logging (Current)
- **File-based**: All logs stored in `backend/logs/`
- **Real-time**: Use `tail -f logs/*.log` for live monitoring
- **Searchable**: `grep`, `awk`, `sed` for log analysis
- **Frontend**: Browser console + localStorage persistence

### 🚀 Future Log Service Integration
Planned support for cloud logging services:
- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Datadog** - Application monitoring and log analysis
- **Papertrail** - Simple cloud logging
- **AWS CloudWatch** - AWS-native logging
- **Google Cloud Logging** - GCP logging service

### 📈 Log Analysis Tools
```bash
# Current local tools
tail -f logs/app.log              # Real-time monitoring
grep "ERROR" logs/*.log           # Error detection
awk '{print $1, $7}' logs/api.log   # Extract timing data
wc -l logs/*.log                  # Log volume analysis

# Future cloud service integration
# ELK: Kibana dashboards for log visualization
# Datadog: APM integration with traces
# CloudWatch: Metrics and alarms
```

### 🐛 Troubleshooting with Logs
```bash
# Backend issues
tail -f logs/errors.log           # Check for errors
grep "meeting_id" logs/api.log     # Trace specific meeting
grep "SECURITY_EVENT" logs/security.log  # Security issues

# Frontend issues
window.logger.getLogs()            # Recent browser logs
window.logger.exportLogs()         # Download for analysis
```
