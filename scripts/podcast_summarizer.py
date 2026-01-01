#!/usr/bin/env python3
"""
Podcast Summarizer
Generates summaries and insights from transcribed podcast episodes using Claude API.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional
import subprocess


class PodcastSummarizer:
    def __init__(
        self,
        input_dir: str = "podcast_transcripts",
        output_dir: str = "podcast_summaries",
        api_key: Optional[str] = None
    ):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")

        if not self.api_key:
            raise ValueError(
                "Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable "
                "or use --api-key flag."
            )

    def get_client(self):
        """Get Anthropic client."""
        try:
            from anthropic import Anthropic
        except ImportError:
            print("Installing anthropic package...")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "anthropic"],
                check=True
            )
            from anthropic import Anthropic

        return Anthropic(api_key=self.api_key)

    def summarize_transcript(
        self,
        transcript: str,
        episode_title: str,
        summary_type: str = "comprehensive"
    ) -> Dict:
        """Generate summary using Claude API."""
        client = self.get_client()

        prompts = {
            "comprehensive": """Analysera detta podcast-avsnitt och skapa en strukturerad sammanfattning:

TITEL: {title}

TRANSKRIPTION:
{transcript}

Skapa en sammanfattning med följande delar:

1. SAMMANFATTNING (2-3 meningar)
   - Vad handlar avsnittet om?

2. HUVUDTEMAN (bullet points)
   - Vilka är de viktigaste ämnena?

3. VIKTIGA INSIKTER (bullet points)
   - Vilka nyckelbudskap eller slutsatser presenteras?

4. EXEMPEL OCH CITAT
   - Intressanta exempel eller citat som illustrerar poänger

5. RELEVANS FÖR SAMHÄLLSVETENSKAP
   - Hur kopplar detta till samhällsvetenskaplig forskning och teori?

6. DISKUSSIONSFRÅGOR
   - 3-5 frågor för vidare reflektion

Skriv på svenska och var konkret och pedagogisk.""",

            "brief": """Sammanfatta detta podcast-avsnitt kortfattat:

TITEL: {title}

TRANSKRIPTION:
{transcript}

Skapa en kort sammanfattning med:
1. ÖVERSIKT (3-4 meningar)
2. HUVUDPOÄNGER (3-5 bullet points)
3. SLUTSATS (1-2 meningar)

Skriv på svenska.""",

            "academic": """Analysera detta podcast-avsnitt ur ett akademiskt perspektiv:

TITEL: {title}

TRANSKRIPTION:
{transcript}

Analysera enligt följande:

1. TEORETISKA RAMVERK
   - Vilka teoretiska perspektiv används eller diskuteras?

2. FORSKNINGSOMRÅDEN
   - Vilka forskningsområden berörs?

3. METODOLOGISKA ASPEKTER
   - Diskuteras forskningsmetoder eller ansatser?

4. SAMHÄLLSRELEVANS
   - Vilka samhällsfrågor belyses?

5. KÄLLOR OCH REFERENSER
   - Nämns specifika forskare, studier eller teorier?

6. KRITISKA REFLEKTIONER
   - Finns olika perspektiv eller kontroverser?

Skriv på svenska med akademisk precision."""
        }

        prompt = prompts.get(summary_type, prompts["comprehensive"]).format(
            title=episode_title,
            transcript=transcript[:100000]  # Limit to ~100k chars to fit context
        )

        print(f"Generating {summary_type} summary with Claude...")

        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4096,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        summary = message.content[0].text

        return {
            "episode_title": episode_title,
            "summary_type": summary_type,
            "summary": summary,
            "model": message.model,
            "tokens_used": message.usage.input_tokens + message.usage.output_tokens
        }

    def summarize_file(
        self,
        transcript_file: Path,
        summary_types: List[str] = ["comprehensive"]
    ) -> List[Dict]:
        """Summarize a single transcript file."""
        try:
            # Load transcript
            with open(transcript_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            transcript_text = data.get('text', '')
            if not transcript_text:
                print(f"✗ No text found in {transcript_file.name}")
                return []

            episode_title = transcript_file.stem

            results = []
            for summary_type in summary_types:
                print(f"Creating {summary_type} summary for: {episode_title}")

                summary_result = self.summarize_transcript(
                    transcript_text,
                    episode_title,
                    summary_type
                )

                # Save summary
                output_file = self.output_dir / f"{episode_title}_{summary_type}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(summary_result, f, indent=2, ensure_ascii=False)

                # Save as markdown for readability
                md_file = self.output_dir / f"{episode_title}_{summary_type}.md"
                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write(f"# {episode_title}\n\n")
                    f.write(f"**Sammanfattningstyp:** {summary_type}\n\n")
                    f.write("---\n\n")
                    f.write(summary_result['summary'])
                    f.write(f"\n\n---\n\n*Genererad med {summary_result['model']}*\n")
                    f.write(f"*Tokens: {summary_result['tokens_used']}*\n")

                print(f"✓ Saved to: {output_file}")
                print(f"✓ Saved to: {md_file}")

                results.append({
                    'episode': episode_title,
                    'type': summary_type,
                    'json_file': str(output_file),
                    'md_file': str(md_file),
                    'tokens': summary_result['tokens_used']
                })

            return results

        except Exception as e:
            print(f"✗ Error summarizing {transcript_file.name}: {e}")
            return []

    def summarize_all(self, summary_types: List[str] = ["comprehensive"]) -> List[Dict]:
        """Summarize all transcript files."""
        transcript_files = list(self.input_dir.glob("*.json"))
        # Exclude metadata file
        transcript_files = [f for f in transcript_files if f.name != "transcripts_metadata.json"]

        if not transcript_files:
            print(f"No transcript files found in {self.input_dir}")
            return []

        print(f"Found {len(transcript_files)} transcript files")
        print(f"Summary types: {', '.join(summary_types)}")

        all_results = []
        total_tokens = 0

        for i, transcript_file in enumerate(transcript_files, 1):
            print(f"\n[{i}/{len(transcript_files)}] Processing: {transcript_file.name}")
            results = self.summarize_file(transcript_file, summary_types)
            all_results.extend(results)
            total_tokens += sum(r['tokens'] for r in results)

        # Save metadata
        metadata_file = self.output_dir / "summaries_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump({
                'total_summaries': len(all_results),
                'total_episodes': len(transcript_files),
                'summary_types': summary_types,
                'total_tokens': total_tokens,
                'summaries': all_results
            }, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Metadata saved to: {metadata_file}")
        return all_results


def main():
    parser = argparse.ArgumentParser(
        description="Summarize podcast transcripts using Claude API"
    )
    parser.add_argument(
        "-i", "--input",
        default="podcast_transcripts",
        help="Input directory with transcript files (default: podcast_transcripts)"
    )
    parser.add_argument(
        "-o", "--output",
        default="podcast_summaries",
        help="Output directory for summaries (default: podcast_summaries)"
    )
    parser.add_argument(
        "-t", "--type",
        action="append",
        choices=["comprehensive", "brief", "academic"],
        help="Summary type(s) to generate (can specify multiple)"
    )
    parser.add_argument(
        "--api-key",
        help="Anthropic API key (or set ANTHROPIC_API_KEY env var)"
    )

    args = parser.parse_args()

    # Default to comprehensive if no type specified
    summary_types = args.type if args.type else ["comprehensive"]

    try:
        summarizer = PodcastSummarizer(
            input_dir=args.input,
            output_dir=args.output,
            api_key=args.api_key
        )

        results = summarizer.summarize_all(summary_types)

        if results:
            total_tokens = sum(r['tokens'] for r in results)
            print(f"\n{'='*60}")
            print(f"✓ Generated {len(results)} summaries")
            print(f"✓ Total tokens used: {total_tokens:,}")
            print(f"✓ Summaries saved to: {summarizer.output_dir}")
            print(f"{'='*60}")
        else:
            print("\n✗ No summaries generated")
            sys.exit(1)

    except ValueError as e:
        print(f"✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
