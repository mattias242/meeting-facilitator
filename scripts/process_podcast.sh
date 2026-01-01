#!/bin/bash
set -e

# Default values
PODCAST_URL=${1:-"https://soundcloud.com/samhallsvetarpodden"}
LIMIT=${2:-5}
USE_LOCAL=${3:-"false"}

echo "=========================================="
echo "Podcast Processing Pipeline"
echo "=========================================="
echo "URL: $PODCAST_URL"
echo "Limit: $LIMIT episodes"
echo "Transcription: $([ "$USE_LOCAL" = "true" ] && echo "Local Whisper" || echo "Whisper API")"
echo ""

# Check for required API keys
if [ "$USE_LOCAL" != "true" ] && [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: OPENAI_API_KEY not set. Will use local Whisper."
    USE_LOCAL="true"
fi

if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ Error: ANTHROPIC_API_KEY not set."
    echo "Please set it: export ANTHROPIC_API_KEY='sk-ant-...'"
    exit 1
fi

# 1. Download
echo "[1/3] Downloading episodes..."
python scripts/podcast_downloader.py \
  "$PODCAST_URL" \
  --name "Samhällsvetarpodden" \
  --limit "$LIMIT"

if [ $? -ne 0 ]; then
    echo "❌ Download failed"
    exit 1
fi

# 2. Transcribe
echo ""
echo "[2/3] Transcribing with Whisper..."
if [ "$USE_LOCAL" = "true" ]; then
    python scripts/podcast_transcriber.py --local --model base
else
    python scripts/podcast_transcriber.py
fi

if [ $? -ne 0 ]; then
    echo "❌ Transcription failed"
    exit 1
fi

# 3. Summarize
echo ""
echo "[3/3] Generating summaries with Claude..."
python scripts/podcast_summarizer.py \
  --type comprehensive \
  --type academic

if [ $? -ne 0 ]; then
    echo "❌ Summarization failed"
    exit 1
fi

echo ""
echo "=========================================="
echo "✓ Processing complete!"
echo "=========================================="
echo ""
echo "📁 Output directories:"
echo "   • Summaries:    podcast_summaries/"
echo "   • Transcripts:  podcast_transcripts/"
echo "   • Audio files:  podcast_downloads/"
echo ""
echo "📖 Read summaries:"
echo "   cat podcast_summaries/*_comprehensive.md"
echo ""
echo "📊 View metadata:"
echo "   cat podcast_summaries/summaries_metadata.json | jq"
echo ""
