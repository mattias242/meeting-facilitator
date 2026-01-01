# Snabbstart: Ladda ner och analysera Samhällsvetarpodden

## 🚀 Snabbaste sättet (ett kommando)

```bash
# Sätt dina API-nycklar
export ANTHROPIC_API_KEY="sk-ant-..."  # Obligatorisk för sammanfattningar
export OPENAI_API_KEY="sk-..."         # Valfri, används för snabbare transkription

# Kör allt (laddar ner 5 episoder)
./scripts/process_podcast.sh "https://soundcloud.com/samhallsvetarpodden" 5
```

**Output**: Kompletta sammanfattningar i `podcast_summaries/`

## 📋 Steg-för-steg (mer kontroll)

### 1. Hitta SoundCloud-länken

Öppna https://soundcloud.com/samhallsvetarpodden i din webbläsare och kopiera URL:en.

Alternativt, om du har RSS-feeden, använd den istället.

### 2. Ladda ner episoder

```bash
python scripts/podcast_downloader.py \
  "https://soundcloud.com/samhallsvetarpodden" \
  --limit 3 \
  --name "Samhällsvetarpodden"
```

**Resultat**: MP3-filer i `podcast_downloads/`

### 3. Transkribera

**Alternativ A: API (snabbt, kostar ~$0.36 per 60 min)**
```bash
export OPENAI_API_KEY="sk-..."
python scripts/podcast_transcriber.py
```

**Alternativ B: Lokalt (gratis, långsammare)**
```bash
python scripts/podcast_transcriber.py --local --model base
```

**Resultat**: Transkriptioner i `podcast_transcripts/`

### 4. Sammanfatta

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
python scripts/podcast_summarizer.py --type comprehensive --type academic
```

**Resultat**: Sammanfattningar i `podcast_summaries/`

### 5. Läs sammanfattningarna

```bash
# Visa alla sammanfattningar
ls -lh podcast_summaries/*.md

# Läs en specifik sammanfattning
cat podcast_summaries/*_comprehensive.md

# Öppna i din editor
code podcast_summaries/  # VS Code
open podcast_summaries/  # macOS
```

## 💰 Kostnadsuppskattning

| Steg | Metod | Kostnad per 60 min | 10 episoder |
|------|-------|-------------------|-------------|
| Transkription | Whisper API | $0.36 | $3.60 |
| Transkription | Lokal Whisper | $0 | $0 |
| Sammanfattning | Claude API | $0.30 | $3.00 |
| **Total** | **API** | **$0.66** | **$6.60** |
| **Total** | **Lokal + Claude** | **$0.30** | **$3.00** |

## 📝 Sammanfattningstyper

### Comprehensive (standard)
Omfattande analys med huvudteman, insikter, citat, och diskussionsfrågor.

```bash
python scripts/podcast_summarizer.py --type comprehensive
```

### Academic
Akademisk analys med teoretiska ramverk, forskningsområden, och metodologi.

```bash
python scripts/podcast_summarizer.py --type academic
```

### Brief
Kortfattad sammanfattning med översikt och huvudpoänger.

```bash
python scripts/podcast_summarizer.py --type brief
```

### Alla på en gång
```bash
python scripts/podcast_summarizer.py \
  --type comprehensive \
  --type academic \
  --type brief
```

## 🔧 Felsökning

### "No such file or directory: podcast_downloads"
Du behöver köra nedladdningssteget först:
```bash
python scripts/podcast_downloader.py "URL"
```

### "yt-dlp not found"
Scriptet installerar automatiskt, men du kan också:
```bash
pip install yt-dlp
```

### "ANTHROPIC_API_KEY not set"
Sätt din API-nyckel:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
# Eller lägg till i backend/.env
echo "ANTHROPIC_API_KEY=sk-ant-..." >> backend/.env
```

### SoundCloud-nedladdning fungerar inte
- Prova färre episoder: `--limit 1`
- Kontrollera att URL:en är korrekt
- Vissa podcasts kan vara privata eller ha nedladdningsbegränsningar

### Lokal Whisper kraschar
Du kan behöva mer RAM. Prova mindre modell:
```bash
python scripts/podcast_transcriber.py --local --model tiny
```

## 🎯 Exempel: Analysera senaste avsnittet

```bash
# Ladda ner endast senaste avsnittet
python scripts/podcast_downloader.py \
  "https://soundcloud.com/samhallsvetarpodden" \
  --limit 1

# Transkribera lokalt (gratis)
python scripts/podcast_transcriber.py --local --model small

# Skapa akademisk analys
export ANTHROPIC_API_KEY="sk-ant-..."
python scripts/podcast_summarizer.py --type academic

# Läs analysen
cat podcast_summaries/*_academic.md
```

## 📚 Mer information

Se [scripts/README_PODCAST.md](scripts/README_PODCAST.md) för detaljerad dokumentation.

## 🎓 Integration med Meeting Facilitator

Dessa verktyg delar teknologi med Meeting Facilitator-projektet:
- Samma transkriptionsteknologi (Whisper)
- Samma AI-motor (Claude)
- Liknande analysramverk

Du kan använda både verktygen för att:
- Transkribera möten → Meeting Facilitator
- Analysera podcasts → Dessa scripts
