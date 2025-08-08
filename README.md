# Nexus AI - YouTube Transcript Fetcher

A robust Python application for downloading YouTube video transcripts in multiple formats (JSON, TXT, PDF) with comprehensive error handling and multi-language support.

## Libraries Used

### Core Libraries (Built-in)
- `argparse` - Command-line argument parsing
- `json` - JSON data handling
- `re` - Regular expressions for URL parsing
- `sys` - System-specific parameters and functions
- `urllib.parse` - URL parsing utilities

### External Libraries (Required)
- `youtube_transcript_api` - Primary YouTube transcript fetching
- `pytube` - Fallback YouTube video data extraction
- `beautifulsoup4` - XML parsing for captions
- `reportlab` - PDF generation (optional)

## Project Structure

```
nexus-ai/
├── README.md                           # Project documentation
├── youtube_transcript_fetcher.py       # Main application
├── venv/                              # Python virtual environment
├── .gitignore                         # Git ignore rules
├── interview-mock.json                 # Sample transcript output
├── interview-mock.txt                  # Sample transcript output
├── interview-mock.pdf                  # Sample transcript output
├── resume.json                        # Sample transcript output
├── resume.txt                         # Sample transcript output
├── resume.pdf                         # Sample transcript output
└── rickroll.json                      # Sample transcript output
```

## Application Specifications

### Main Script: `youtube_transcript_fetcher.py`

**Purpose**: Downloads YouTube video transcripts in multiple formats (JSON, TXT, PDF)

**Key Features**:
- Supports multiple YouTube URL formats (standard, short, embed, shorts)
- Multi-language transcript support
- Fallback mechanisms for transcript fetching
- Multiple output formats
- Error handling and user-friendly prompts

### Core Functions

1. **`video_id_from_url(url: str) -> str`**
   - Extracts 11-character video ID from any YouTube URL format
   - Supports: youtu.be, watch?v=, embed/, v/, shorts/

2. **`fetch_with_yta(video_id: str, languages: list[str])`**
   - Primary transcript fetching using youtube-transcript-api
   - No API key required
   - Handles TranscriptsDisabled and NoTranscriptFound exceptions
   - Uses updated API with `fetch()` method and `FetchedTranscript` objects

3. **`fetch_with_pytube(video_id: str, languages: list[str])`**
   - Fallback method using pytube and BeautifulSoup
   - Parses XML captions when API method fails
   - Supports both human and auto-generated captions

4. **`save_as_txt(transcript: list, filename: str) -> bool`**
   - Saves transcript as plain text file
   - UTF-8 encoding support

5. **`save_as_pdf(transcript: list, filename: str) -> bool`**
   - Generates formatted PDF with timestamps
   - Uses ReportLab library
   - Includes title and formatted transcript content

## Installation

### Setup Virtual Environment:
```bash
# Create virtual environment (if not already created)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows
```

### Required Dependencies:
```bash
pip install youtube-transcript-api pytube beautifulsoup4 reportlab
```

### Optional Dependencies:
- `reportlab` - For PDF generation (can be installed separately)

### API Compatibility Notes:
- Updated to work with `youtube-transcript-api` v1.2.2+
- Uses `fetch()` method instead of deprecated `get_transcript()`
- Handles `FetchedTranscript` objects with `snippets` structure

## Usage

### Basic Usage:
```bash
# Activate virtual environment first
source venv/bin/activate

# Run the application
python3 youtube_transcript_fetcher.py --lang en
```

### Command Line Arguments:
- `--lang`: Language code for transcript (default: "en")

### Interactive Prompts:
1. YouTube video URL input
2. Output filename (without extension)

### Supported YouTube URL Formats:
- Standard: `https://www.youtube.com/watch?v=VIDEO_ID`
- Short: `https://youtu.be/VIDEO_ID`
- Embed: `https://www.youtube.com/embed/VIDEO_ID`
- Shorts: `https://youtube.com/shorts/VIDEO_ID`

## Output Formats

The application generates three output files for each transcript:

- **JSON**: Structured data with timestamps and text
- **TXT**: Plain text transcript
- **PDF**: Formatted document with timestamps

### Example Output:
```
✅  JSON transcript saved to: my_video.json
✅  TXT transcript saved to: my_video.txt
✅  PDF transcript saved to: my_video.pdf
🎉  All formats saved successfully!
```

## Error Handling

The application includes comprehensive error handling for:
- Invalid YouTube URLs
- Missing transcripts/captions
- File I/O errors
- Missing dependencies
- Network connectivity issues
- API compatibility issues (handles both old and new API structures)

## Sample Output Files

The project includes several sample transcript files:
- `interview-mock.*` - Interview transcript in 3 formats
- `resume.*` - Resume-related transcript in 3 formats  
- `rickroll.json` - Sample transcript data

## Development Environment

- **Python Version**: 3.x (uses `__future__` annotations)
- **Virtual Environment**: `venv/` directory for dependency isolation
- **OS Support**: Cross-platform (tested on macOS)
- **API Version**: Compatible with `youtube-transcript-api` v1.2.2+

## Git Configuration

The `.gitignore` file excludes:
- Virtual environment (`venv/`)
- All media files (audio/video formats)
- Generated transcript files (JSON, TXT, PDF)

## Recent Updates

### API Compatibility Fixes (Latest):
- **Fixed API Method**: Updated from `get_transcript()` to `fetch()` method
- **Data Structure**: Added support for `FetchedTranscript` objects with `snippets`
- **Backward Compatibility**: Maintains support for both old and new API structures
- **Virtual Environment**: Proper setup and activation instructions

## Future Enhancements

Potential improvements could include:
- Batch processing multiple videos
- Support for subtitle formats (SRT, VTT)
- Audio extraction capabilities
- Web interface
- API integration for automated transcript fetching

## License

This project is open source and available under the MIT License.

---

**Note**: This tool respects YouTube's terms of service and is intended for educational and personal use only. Always ensure you have permission to download and use any transcripts.