# Podcast Downloader, Transcriber och Summarizer

Verktyg för att ladda ner podcast-episoder, transkribera dem och skapa AI-genererade sammanfattningar.

## Snabbstart: Samhällsvetarpodden

```bash
# 1. Ladda ner episoder från SoundCloud
python scripts/podcast_downloader.py \
  "https://soundcloud.com/samhallsvetarpodden" \
  --name "Samhällsvetarpodden" \
  --limit 5

# 2. Transkribera med Whisper
python scripts/podcast_transcriber.py --local

# 3. Sammanfatta med Claude
python scripts/podcast_summarizer.py --type comprehensive --type academic

# Allt i ett kommando:
bash scripts/process_podcast.sh "https://soundcloud.com/samhallsvetarpodden" 5
```

## Installation

### Krav
```bash
# Python 3.11+
python --version

# Backend dependencies (för Claude API)
cd backend
pip install -r requirements.txt

# Script dependencies
pip install yt-dlp openai anthropic
```

### API-nycklar

```bash
# OpenAI för Whisper transkription (API-baserad)
export OPENAI_API_KEY="sk-..."

# Anthropic för Claude sammanfattningar
export ANTHROPIC_API_KEY="sk-ant-..."
```

Eller lägg till i `.env`:
```bash
echo "OPENAI_API_KEY=sk-..." >> backend/.env
echo "ANTHROPIC_API_KEY=sk-ant-..." >> backend/.env
```

## Användning

### 1. Ladda ner episoder

#### Från SoundCloud
```bash
python scripts/podcast_downloader.py \
  "https://soundcloud.com/USER/PODCAST" \
  --output podcast_downloads \
  --limit 10 \
  --name "Podcast Name"
```

#### Från RSS Feed
```bash
python scripts/podcast_downloader.py \
  "https://feeds.example.com/podcast.rss" \
  --output podcast_downloads \
  --limit 10
```

**Parametrar:**
- `url` (obligatorisk): SoundCloud URL eller RSS feed URL
- `--output` / `-o`: Målkatalog (default: podcast_downloads)
- `--limit` / `-n`: Max antal episoder att ladda ner
- `--name`: Podcast-namn för metadata

**Output:**
```
podcast_downloads/
├── Episode 1 Title.mp3
├── Episode 2 Title.mp3
└── metadata.json
```

### 2. Transkribera

#### Med Whisper API (snabbare, kostar pengar)
```bash
export OPENAI_API_KEY="sk-..."
python scripts/podcast_transcriber.py \
  --input podcast_downloads \
  --output podcast_transcripts
```

#### Med lokal Whisper (gratis, långsammare)
```bash
python scripts/podcast_transcriber.py \
  --input podcast_downloads \
  --output podcast_transcripts \
  --local \
  --model base
```

**Whisper-modeller** (för `--local`):
- `tiny` - Snabbast, lägst kvalitet (~1GB RAM)
- `base` - Balanserad (default, ~1GB RAM)
- `small` - Bättre kvalitet (~2GB RAM)
- `medium` - Mycket bra kvalitet (~5GB RAM)
- `large` - Bäst kvalitet (~10GB RAM)

**Output:**
```
podcast_transcripts/
├── Episode 1 Title.json        # Fullständig transkription med timestamps
├── Episode 1 Title.txt         # Ren text
├── Episode 2 Title.json
├── Episode 2 Title.txt
└── transcripts_metadata.json
```

### 3. Sammanfatta

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
python scripts/podcast_summarizer.py \
  --input podcast_transcripts \
  --output podcast_summaries \
  --type comprehensive
```

**Sammanfattningstyper:**

**`comprehensive`** (default) - Omfattande analys med:
- Sammanfattning (2-3 meningar)
- Huvudteman
- Viktiga insikter
- Exempel och citat
- Relevans för samhällsvetenskap
- Diskussionsfrågor

**`brief`** - Kortfattad sammanfattning:
- Översikt (3-4 meningar)
- Huvudpoänger (3-5 punkter)
- Slutsats

**`academic`** - Akademisk analys:
- Teoretiska ramverk
- Forskningsområden
- Metodologiska aspekter
- Samhällsrelevans
- Källor och referenser
- Kritiska reflektioner

**Flera typer samtidigt:**
```bash
python scripts/podcast_summarizer.py \
  --type comprehensive \
  --type brief \
  --type academic
```

**Output:**
```
podcast_summaries/
├── Episode 1 Title_comprehensive.json
├── Episode 1 Title_comprehensive.md    # Läsbar markdown
├── Episode 1 Title_academic.json
├── Episode 1 Title_academic.md
└── summaries_metadata.json
```

## Komplett Workflow

### Automatisk process för Samhällsvetarpodden

Skapa ett script `scripts/process_podcast.sh`:

```bash
#!/bin/bash
set -e

PODCAST_URL=${1:-"https://soundcloud.com/samhallsvetarpodden"}
LIMIT=${2:-5}

echo "=========================================="
echo "Podcast Processing Pipeline"
echo "=========================================="
echo "URL: $PODCAST_URL"
echo "Limit: $LIMIT episodes"
echo ""

# 1. Download
echo "[1/3] Downloading episodes..."
python scripts/podcast_downloader.py \
  "$PODCAST_URL" \
  --name "Samhällsvetarpodden" \
  --limit "$LIMIT"

# 2. Transcribe (using API for speed)
echo ""
echo "[2/3] Transcribing with Whisper..."
python scripts/podcast_transcriber.py

# 3. Summarize
echo ""
echo "[3/3] Generating summaries with Claude..."
python scripts/podcast_summarizer.py \
  --type comprehensive \
  --type academic

echo ""
echo "=========================================="
echo "✓ Processing complete!"
echo "=========================================="
echo "Summaries: podcast_summaries/"
echo "Transcripts: podcast_transcripts/"
echo "Audio files: podcast_downloads/"
```

Gör det körbart:
```bash
chmod +x scripts/process_podcast.sh
```

Kör:
```bash
./scripts/process_podcast.sh "https://soundcloud.com/samhallsvetarpodden" 10
```

## Hitta RSS-feed manuellt

### För Samhällsvetarpodden specifikt:

1. **Kolla Podtail**:
   - Gå till https://podtail.se/podcast/samhallsvetarpodden/
   - Leta efter "Prenumerera" eller RSS-ikon
   - Högerklicka och kopiera länk

2. **Kolla SoundCloud**:
   - Om de har SoundCloud (vilket de verkar ha), använd direkt SoundCloud-URL
   - `yt-dlp` hanterar det automatiskt

3. **Inspektera hemsidan**:
   ```bash
   # Om podden finns på en specifik hemsida
   curl -s https://akademssr.se/om-oss/podcasts/samhallsvetarpodden | grep -i rss
   ```

4. **Använda Podcast Apps**:
   - Apple Podcasts: Kopiera RSS-länk från "Share Episode"
   - Spotify: Använd verktyg som https://spotifeed.timdorr.com/

## Kostnadsuppskattning

### Whisper API (transkription)
- **Kostnad**: $0.006 per minut
- **60 min episode**: ~$0.36
- **10 episoder (60 min vardera)**: ~$3.60

### Claude API (sammanfattning)
- **Kostnad**: ~$3 per miljon input tokens, ~$15 per miljon output tokens
- **Omfattande sammanfattning av 60 min transkription**: ~$0.20-0.40
- **10 episoder**: ~$2-4

**Total för 10 episoder: ~$6-8**

### Lokal Whisper (gratis)
- **Kostnad**: $0
- **Tid**: Beror på din dator och modellstorlek
  - `tiny`: ~realtime (60 min = 60 min)
  - `base`: ~2-3x realtime (60 min = 120-180 min)
  - `small`: ~4-5x realtime
  - `medium`: ~8-10x realtime

## Felsökning

### "yt-dlp not found"
Scriptet installerar automatiskt, men du kan också göra:
```bash
pip install yt-dlp
```

### "No audio files found"
Kontrollera att nedladdningen lyckades:
```bash
ls -lh podcast_downloads/
```

### "OpenAI API key not found"
```bash
export OPENAI_API_KEY="sk-..."
# Eller använd --local för lokal transkription
```

### "Anthropic API key not found"
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
# Eller lägg till i backend/.env
```

### Lokal Whisper kraschar
Du kan behöva mer RAM. Prova mindre modell:
```bash
python scripts/podcast_transcriber.py --local --model tiny
```

### SoundCloud-nedladdning misslyckas
Vissa SoundCloud-konton har nedladdningsbegränsningar. Försök:
1. Använd RSS-feed istället
2. Ladda ner färre episoder åt gången
3. Vänta några minuter mellan nedladdningar

## Exempel: Komplett analys av ett avsnitt

```bash
# 1. Ladda ner senaste avsnittet
python scripts/podcast_downloader.py \
  "https://soundcloud.com/samhallsvetarpodden" \
  --limit 1

# 2. Transkribera (lokal för att spara pengar)
python scripts/podcast_transcriber.py --local --model small

# 3. Skapa alla typer av sammanfattningar
python scripts/podcast_summarizer.py \
  --type comprehensive \
  --type brief \
  --type academic

# 4. Läs sammanfattningen
cat podcast_summaries/*_comprehensive.md
```

## Integration med Meeting Facilitator

Dessa verktyg kan integreras med Meeting Facilitator:

1. **Transkriptionsmotor**: Samma Whisper-teknik kan användas för möten
2. **Claude-integration**: Samma sammanfattningslogik
3. **Strukturerad analys**: Liknande analysramverk (IDOARRT vs podcastanalys)

Framtida möjligheter:
- Importera podcast-transkriptioner som "virtuella möten"
- Använd GROW-coachingmodellen för att analysera poddinnehåll
- Generera diskussionsfrågor för studiecirklar

## Ytterligare resurser

- **yt-dlp dokumentation**: https://github.com/yt-dlp/yt-dlp
- **Whisper API**: https://platform.openai.com/docs/guides/speech-to-text
- **Claude API**: https://docs.anthropic.com/claude/reference/
- **Podcast RSS-format**: https://help.apple.com/itc/podcasts_connect/
