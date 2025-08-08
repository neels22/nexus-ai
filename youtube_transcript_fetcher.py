#!/usr/bin/env python3
"""
Fetch and save a YouTube video's transcript as JSON, TXT, and PDF files.

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
        api = YouTubeTranscriptApi()
        return api.fetch(video_id, languages=languages)
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

def save_as_txt(transcript: list, filename: str) -> bool:
    """Save transcript as plain text file."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            for entry in transcript:
                f.write(f"{entry['text']}\n")
        return True
    except Exception as e:
        print(f"❌  Error saving TXT file: {e}")
        return False

def save_as_pdf(transcript: list, filename: str) -> bool:
    """Save transcript as PDF file."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        
        # Create a custom style for transcript text
        transcript_style = ParagraphStyle(
            'TranscriptStyle',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            leading=14
        )
        
        story = []
        
        # Add title
        title = Paragraph("YouTube Video Transcript", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Add transcript content
        for entry in transcript:
            text = entry['text']
            # Format timestamp (convert seconds to MM:SS)
            minutes = int(entry['start'] // 60)
            seconds = int(entry['start'] % 60)
            timestamp = f"[{minutes:02d}:{seconds:02d}]"
            
            # Combine timestamp and text
            full_text = f"{timestamp} {text}"
            p = Paragraph(full_text, transcript_style)
            story.append(p)
        
        doc.build(story)
        return True
        
    except ImportError:
        print("❌  PDF generation requires reportlab. Install with: pip install reportlab")
        return False
    except Exception as e:
        print(f"❌  Error saving PDF file: {e}")
        return False

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
    filename = input("Enter filename to save transcript (without extension): ").strip()
    
    if not filename:
        print("❌  No filename provided. Exiting.")
        sys.exit(1)

    langs = [args.lang]

    print(f"Fetching transcript for video ID: {vid}")
    transcript = fetch_with_yta(vid, langs) or fetch_with_pytube(vid, langs)
    if transcript is None:
        sys.exit("❌  No transcript or captions available for this video.")

    # Save to all three formats
    success_count = 0
    
    # Convert FetchedTranscript to list of dicts for compatibility
    if hasattr(transcript, 'snippets'):
        # New API structure
        transcript_list = [
            {
                'text': snippet.text,
                'start': snippet.start,
                'duration': snippet.duration
            }
            for snippet in transcript.snippets
        ]
    else:
        # Old API structure (fallback)
        transcript_list = transcript
    
    # Save as JSON
    json_filename = filename + '.json'
    try:
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(transcript_list, f, ensure_ascii=False, indent=2)
        print(f"✅  JSON transcript saved to: {json_filename}")
        success_count += 1
    except Exception as e:
        print(f"❌  Error saving JSON file: {e}")
    
    # Save as TXT
    txt_filename = filename + '.txt'
    if save_as_txt(transcript_list, txt_filename):
        print(f"✅  TXT transcript saved to: {txt_filename}")
        success_count += 1
    
    # Save as PDF
    pdf_filename = filename + '.pdf'
    if save_as_pdf(transcript_list, pdf_filename):
        print(f"✅  PDF transcript saved to: {pdf_filename}")
        success_count += 1
    
    if success_count == 0:
        print("❌  Failed to save transcript in any format.")
        sys.exit(1)
    elif success_count < 3:
        print(f"⚠️  Successfully saved {success_count}/3 formats.")
    else:
        print("🎉  All formats saved successfully!")

if __name__ == "__main__":
    main()
