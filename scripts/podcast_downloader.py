#!/usr/bin/env python3
"""
Podcast Downloader and Processor
Downloads podcast episodes from SoundCloud/RSS and prepares them for transcription.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Optional
import urllib.request
import xml.etree.ElementTree as ET


class PodcastDownloader:
    def __init__(self, output_dir: str = "podcast_downloads"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def check_ytdlp_installed(self) -> bool:
        """Check if yt-dlp is installed."""
        try:
            subprocess.run(
                ["yt-dlp", "--version"],
                capture_output=True,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def install_ytdlp(self):
        """Install yt-dlp using pip."""
        print("Installing yt-dlp...")
        subprocess.run([sys.executable, "-m", "pip", "install", "yt-dlp"], check=True)
        print("yt-dlp installed successfully!")

    def get_rss_feed_info(self, rss_url: str) -> Dict:
        """Parse RSS feed and extract episode information."""
        print(f"Fetching RSS feed: {rss_url}")

        with urllib.request.urlopen(rss_url) as response:
            xml_data = response.read()

        root = ET.fromstring(xml_data)
        channel = root.find('channel')

        podcast_info = {
            'title': channel.find('title').text if channel.find('title') is not None else 'Unknown',
            'description': channel.find('description').text if channel.find('description') is not None else '',
            'episodes': []
        }

        for item in channel.findall('item'):
            title = item.find('title')
            enclosure = item.find('enclosure')
            pub_date = item.find('pubDate')
            description = item.find('description')

            if enclosure is not None:
                episode = {
                    'title': title.text if title is not None else 'Untitled',
                    'url': enclosure.get('url'),
                    'pub_date': pub_date.text if pub_date is not None else '',
                    'description': description.text if description is not None else ''
                }
                podcast_info['episodes'].append(episode)

        return podcast_info

    def download_from_soundcloud(self, url: str, limit: Optional[int] = None) -> List[Path]:
        """Download episodes from SoundCloud using yt-dlp."""
        if not self.check_ytdlp_installed():
            print("yt-dlp not found. Installing...")
            self.install_ytdlp()

        cmd = [
            "yt-dlp",
            "-x",  # Extract audio
            "--audio-format", "mp3",
            "--embed-thumbnail",
            "--add-metadata",
            "--output", str(self.output_dir / "%(title)s.%(ext)s"),
            "--print", "after_move:filepath",
            "--no-warnings"
        ]

        if limit:
            cmd.extend(["--playlist-end", str(limit)])

        cmd.append(url)

        print(f"Downloading from SoundCloud: {url}")
        print(f"Saving to: {self.output_dir}")

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Error downloading: {result.stderr}")
            return []

        # Parse output to get downloaded file paths
        downloaded_files = [
            Path(line.strip())
            for line in result.stdout.split('\n')
            if line.strip() and Path(line.strip()).exists()
        ]

        return downloaded_files

    def download_from_rss(self, rss_url: str, limit: Optional[int] = None) -> List[Path]:
        """Download episodes from RSS feed."""
        podcast_info = self.get_rss_feed_info(rss_url)

        print(f"\nPodcast: {podcast_info['title']}")
        print(f"Found {len(podcast_info['episodes'])} episodes")

        episodes_to_download = podcast_info['episodes'][:limit] if limit else podcast_info['episodes']

        downloaded_files = []

        for i, episode in enumerate(episodes_to_download, 1):
            print(f"\n[{i}/{len(episodes_to_download)}] Downloading: {episode['title']}")

            # Sanitize filename
            safe_title = "".join(c for c in episode['title'] if c.isalnum() or c in (' ', '-', '_')).strip()
            filename = self.output_dir / f"{safe_title}.mp3"

            try:
                urllib.request.urlretrieve(episode['url'], filename)
                downloaded_files.append(filename)
                print(f"✓ Saved to: {filename}")
            except Exception as e:
                print(f"✗ Error downloading {episode['title']}: {e}")

        return downloaded_files

    def save_metadata(self, files: List[Path], podcast_name: str):
        """Save metadata about downloaded episodes."""
        metadata = {
            'podcast': podcast_name,
            'episodes': [
                {
                    'filename': str(f.name),
                    'path': str(f),
                    'size_mb': f.stat().st_size / (1024 * 1024)
                }
                for f in files
            ],
            'total_episodes': len(files),
            'total_size_mb': sum(f.stat().st_size for f in files) / (1024 * 1024)
        }

        metadata_file = self.output_dir / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Metadata saved to: {metadata_file}")
        return metadata


def main():
    parser = argparse.ArgumentParser(
        description="Download podcast episodes for transcription and summarization"
    )
    parser.add_argument(
        "url",
        help="SoundCloud URL or RSS feed URL"
    )
    parser.add_argument(
        "-o", "--output",
        default="podcast_downloads",
        help="Output directory (default: podcast_downloads)"
    )
    parser.add_argument(
        "-n", "--limit",
        type=int,
        help="Limit number of episodes to download"
    )
    parser.add_argument(
        "--name",
        default="podcast",
        help="Podcast name for metadata"
    )

    args = parser.parse_args()

    downloader = PodcastDownloader(args.output)

    # Determine if URL is RSS or SoundCloud
    if args.url.endswith('.rss') or args.url.endswith('.xml') or 'feeds.soundcloud.com' in args.url:
        downloaded_files = downloader.download_from_rss(args.url, args.limit)
    else:
        # Assume SoundCloud or other yt-dlp compatible URL
        downloaded_files = downloader.download_from_soundcloud(args.url, args.limit)

    if downloaded_files:
        metadata = downloader.save_metadata(downloaded_files, args.name)
        print(f"\n{'='*60}")
        print(f"✓ Downloaded {metadata['total_episodes']} episodes")
        print(f"✓ Total size: {metadata['total_size_mb']:.2f} MB")
        print(f"✓ Location: {downloader.output_dir}")
        print(f"{'='*60}")
        print("\nNext steps:")
        print("1. Run transcription: python scripts/podcast_transcriber.py")
        print("2. Generate summaries: python scripts/podcast_summarizer.py")
    else:
        print("\n✗ No files were downloaded")
        sys.exit(1)


if __name__ == "__main__":
    main()
