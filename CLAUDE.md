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

1. **Single meeting at a time** - No concurrent meeting support
2. **Swedish language only** - Transcription and questions in Swedish
3. **No speaker diarization** - Can't identify who said what
4. **Development security** - Basic security implemented, production hardening needed

## 🔒 Security Status

### ✅ Implemented (Phase 1)
- **JWT Authentication**: All API endpoints protected
- **Database Encryption**: Audio, transcriptions, protocols encrypted at rest
- **Input Validation**: Strict Pydantic schemas with security checks
- **File Upload Security**: MIME type validation, size limits, content scanning
- **WebSocket Security**: Token-based authentication
- **TDD Framework**: Complete test infrastructure with CI/CD

### 🔄 In Progress (Phase 2)
- Rate limiting implementation
- Enhanced error handling
- Security headers (CSP, HSTS)
- Audit logging

### 📋 Security Requirements
See [AUDIT.md](AUDIT.md) for complete security analysis and roadmap.

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

## 🚀 Next Steps

### Phase 1 Complete ✅
- [x] Critical security vulnerabilities fixed
- [x] Authentication system implemented
- [x] Database encryption deployed
- [x] TDD framework established
- [x] Pure trunk-based development workflow

### Phase 2 - Production Hardening (Next 2-4 weeks)
- [ ] Rate limiting implementation
- [ ] Security headers (CSP, HSTS)
- [ ] Enhanced error handling
- [ ] Audit logging system
- [ ] Production deployment guide

### Phase 3 - Advanced Features (1-2 months)
- [ ] Multi-language support
- [ ] Speaker diarization
- [ ] Voice synthesis
- [ ] Advanced analytics
- [ ] Enterprise security features

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
