# Meeting Facilitator AI 🤖

En AI-driven mötesassistent som aktivt deltar i fysiska möten genom att använda IDOARRT-ramverket och GROW-coachingmodellen för att facilitera och coacha grupper mot sina mål.

## ✨ Features

- **IDOARRT-strukturering**: Använder beprövat ramverk för mötesplanering
- **Real-time transkribering**: Spelar in och transkriberar möten i 2-minuters chunks
- **Smart facilitering**: AI-genererade coaching-frågor baserade på GROW-modellen
- **Intelligent triggers**: Automatisk detektering av:
  - Tidsvarningar (50%, 75%, 5min kvar)
  - Målavvikelse (diskussionen spårar ur)
  - Perspektivluckor (bara 1-2 personer pratar)
  - Komplexitetsmisstag (fel approach för problemtyp)
- **Automatiskt protokoll**: Genererar strukturerad sammanfattning och måluppfyllnadsbedömning

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Frontend     │────▶│     Backend     │────▶│    Database     │
│  React + TS     │◀────│   FastAPI       │     │    SQLite       │
│  Web Audio API  │  WS │   Claude API    │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

**Tech Stack**:
- Frontend: React 18 + TypeScript + Vite
- Backend: FastAPI (Python 3.11+) + SQLAlchemy
- Database: SQLite
- AI: Claude Sonnet API (Anthropic)
- Real-time: WebSocket

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Anthropic API key ([get one here](https://console.anthropic.com/))

### Installation

1. **Clone the repository**
   ```bash
   cd meeting-facilitator
   ```

2. **Setup Backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt

   # Setup environment
   cp .env.example .env
   # Edit .env and add your ANTHROPIC_API_KEY
   ```

3. **Setup Frontend**
   ```bash
   cd ../frontend
   npm install

   # Setup environment
   cp .env.example .env
   ```

4. **Start the Application**

   Terminal 1 (Backend):
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn app.main:app --reload --port 8000
   ```

   Terminal 2 (Frontend):
   ```bash
   cd frontend
   npm run dev
   ```

5. **Access the Application**
   - Frontend: http://localhost:5173
   - Backend API docs: http://localhost:8000/docs

## 📖 Usage

### 1. Förberedelsefasen

1. Skapa en IDOARRT-fil (se [IDOARRT format guide](docs/IDOARRT-format.md))
2. Ladda upp filen i applikationen
3. Granska parsed data
4. Klicka "Starta Möte"

**Exempel IDOARRT-fil**:
```markdown
# Intent
Planera Q2 produktstrategi

# Desired Outcomes
- Beslutade prioriteringar för Q2
- Resurstilldelning klar
- Tydlig tidsplan

# Agenda
1. Q1 Review (15 min)
2. Q2 Brainstorming (20 min)
3. Prioritering (15 min)
4. Resursplanering (10 min)

# Roles
- Facilitator: Anna
- Timekeeper: Björn

# Rules
- En person i taget
- Fokusera på lösningar
- Använd parkering för sidospår

# Time
Total: 60 minutes
```

### 2. Live-Mötet

- **Audio Recording**: Mötet spelas in automatiskt i 2-minuters chunks
- **Transkribering**: Varje chunk transkriberas med Claude API
- **Interventioner**: Assistenten ger faciliterande frågor när:
  - Tiden börjar ta slut
  - Diskussionen spårar ur från målen
  - Bara några få pratar
  - Fel komplexitetsapproach används
- **Deltagare kan svara**: Via input-fönstret (framtida feature: röststyrning)

### 3. Avslutningsfasen

När mötet avslutas genereras automatiskt:
- Fullständig transkribering
- Sammanfattning per agenda-punkt
- Måluppfyllnadsbedömning
- Beslut och action items
- Exporterbart protokoll (markdown)

## 🧪 Development

### Run Tests

Backend:
```bash
cd backend
pytest
```

Frontend:
```bash
cd frontend
npm test
```

### Code Quality

Backend:
```bash
ruff check .      # Linting
mypy app/         # Type checking
```

Frontend:
```bash
npm run typecheck  # TypeScript
npm run lint       # ESLint
```

## 📚 Documentation

- [IDOARRT Format Guide](docs/IDOARRT-format.md) - Detaljerad spec för IDOARRT-filer
- [CLAUDE.md](CLAUDE.md) - Development guide för contributors
- [API Documentation](http://localhost:8000/docs) - Interactive API docs (när backend körs)

## 🔧 Configuration

### Backend Environment Variables

```bash
# .env in backend/
ANTHROPIC_API_KEY=sk-ant-...       # Required
DATABASE_URL=sqlite:///./meeting.db
CORS_ORIGINS=http://localhost:5173
```

### Frontend Environment Variables

```bash
# .env in frontend/
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

## 🤝 Contributing

Se [CLAUDE.md](CLAUDE.md) för utvecklingsinstruktioner.

### Development Workflow

1. Läs [CLAUDE.md](CLAUDE.md) för projektstruktur och konventioner
2. Skapa en branch för din feature
3. Implementera enligt planen i CLAUDE.md
4. Kör tests och quality checks
5. Skapa pull request

## 🐛 Troubleshooting

### Backend startar inte
- Kontrollera Python-version: `python --version` (måste vara 3.11+)
- Verifiera virtual environment är aktiverat
- Kolla att alla dependencies är installerade

### Frontend kan inte ansluta till backend
- Verifiera att backend körs på port 8000
- Kolla CORS-inställningar i `backend/app/main.py`
- Kontrollera att `.env`-filer finns

### Audio recording fungerar inte
- Webbläsaren måste stödja MediaRecorder API (Chrome, Firefox, Edge)
- Användaren måste ge mikrofontillstånd
- Kolla browser console för felmeddelanden

### Claude API errors
- Verifiera `ANTHROPIC_API_KEY` i `backend/.env`
- Kontrollera API rate limits
- Granska error messages i backend logs

## 📋 Known Limitations

- **Single meeting at a time** - Ingen concurrency-support ännu
- **Swedish only** - Transkribering och frågor på svenska
- **No speaker diarization** - Kan inte identifiera vem som sa vad
- **Local deployment only** - Ej produktionsklar

## 🚧 Future Roadmap

- [ ] Multi-language support
- [ ] Speaker identification (ML-based diarization)
- [ ] Voice synthesis för assistentens frågor
- [ ] Remote/hybrid meeting support
- [ ] Calendar integration
- [ ] Analytics dashboard
- [ ] Mobile app för deltagare

## 📄 License

MIT

## 👥 Authors

Built with Claude Code and the project-scaffolder toolkit.

## 🙏 Acknowledgments

- **IDOARRT Framework**: För strukturerad mötesplanering
- **GROW Model**: För coachande facilitering
- **Anthropic**: För Claude API
- **FastAPI**: För excellent Python web framework
- **React**: För robust frontend development
