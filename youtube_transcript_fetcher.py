#!/usr/bin/env python3
"""
Fetch and save a YouTube video's transcript as JSON file.

Usage:
  python youtube_transcript_fetcher.py --lang en
  # Then enter the YouTube URL and filename when prompted
"""

from __future__ import annotations
import argparse, json, re, sys
from urllib.parse import urlparse, parse_qs

# ---------- helpers ----------------------------------------------------------
def video_id_from_url(url: str) -> str:
    """Extracts the 11-character video ID from any common YouTube URL."""
    parsed = urlparse(url)
    if parsed.hostname in ("youtu.be",):
        return parsed.path.lstrip("/")
    if "watch" in parsed.path and "v" in parse_qs(parsed.query):
        return parse_qs(parsed.query)["v"][0]
    # short or embed link
    m = re.search(r"(?:embed/|v/|shorts/)([0-9A-Za-z_-]{11})", url)
    if m:
        return m.group(1)
    raise ValueError("Could not determine video ID from URL.")

def fetch_with_yta(video_id: str, languages: list[str]):
    """Try youtube-transcript-api first (no API key needed)."""
    from youtube_transcript_api import (
        YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound,
    )
    try:
        return YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
    except (TranscriptsDisabled, NoTranscriptFound):
        return None  # let caller decide next steps

def fetch_with_pytube(video_id: str, languages: list[str]):
    """Fallback: pull caption XML via pytube & strip tags with BeautifulSoup."""
    from pytube import YouTube
    from bs4 import BeautifulSoup

    yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
    for code in languages + [f"a.{languages[0]}"]:           # try human then auto
        caption = yt.captions.get(code)
        if caption:
            xml = caption.xml_captions
            soup = BeautifulSoup(xml, "xml")
            return [
                {"text": t.text.strip(), "start": float(t["start"]), "duration": float(t["dur"])}
                for t in soup.find_all("text")
            ]
    return None

# ---------- main -------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Download YouTube transcript.")
    parser.add_argument("--lang", default="en", help="Preferred language code")
    args = parser.parse_args()

    # Prompt for URL input
    print("YouTube Transcript Fetcher")
    print("=" * 30)
    url = input("Enter YouTube video URL: ").strip()
    
    if not url:
        print("❌  No URL provided. Exiting.")
        sys.exit(1)

    try:
        vid = video_id_from_url(url)
    except ValueError as e:
        print(f"❌  Invalid YouTube URL: {e}")
        sys.exit(1)

    # Prompt for filename
    filename = input("Enter filename to save transcript (without .json extension): ").strip()
    
    if not filename:
        print("❌  No filename provided. Exiting.")
        sys.exit(1)
    
    # Add .json extension if not provided
    if not filename.endswith('.json'):
        filename += '.json'

    langs = [args.lang]

    print(f"Fetching transcript for video ID: {vid}")
    transcript = fetch_with_yta(vid, langs) or fetch_with_pytube(vid, langs)
    if transcript is None:
        sys.exit("❌  No transcript or captions available for this video.")

    # Save to file
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(transcript, f, ensure_ascii=False, indent=2)
        print(f"✅  Transcript saved to: {filename}")
    except Exception as e:
        print(f"❌  Error saving file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
