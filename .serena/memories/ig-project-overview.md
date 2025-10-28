# IG Focus Project - Overview

## Project Identity
- **Name**: IG Focus (Instagram Feed Reader & Media Archiver)
- **Location**: `/Users/iagdotme/APPS/ig`
- **Language**: Python 3
- **Primary Library**: instagrapi (Instagram API wrapper)

## Purpose
A Python-based tool to programmatically access, archive, and download content from Instagram feeds. Enables users to:
- Archive Instagram feed posts with full metadata
- Download photos, videos, and album content
- Retrieve comments and engagement data
- Work seamlessly with 2FA-protected accounts

## Core Files

### Main Scripts
1. **feed_reader_enhanced.py** (RECOMMENDED)
   - Most feature-complete implementation
   - Functions: login_user(), extract_post_data(), get_feed_posts(), get_post_comments(), download_media(), display_post_info(), main()
   - Supports: 2FA, media downloads, comment fetching, comprehensive metadata

2. **feed_reader.py** (Basic)
   - Simpler, faster version for quick checks
   - Functions: login_user(), get_feed_posts(), display_post_info(), save_feed_to_json(), save_credentials(), load_credentials(), main()
   - Good for: Users who don't need downloads

3. **login_with_2fa.py** (Auth Utility)
   - Functions: login_with_2fa(), main()
   - Dedicated 2FA authentication handler
   - Creates session.json for subsequent logins

4. **simple_example.py** (Minimal)
   - Basic implementation without 2FA
   - Educational reference

### Documentation
- **README.md** - User documentation
- **CLAUDE.md** - Developer guide (comprehensive)
- **FEATURES.md** - Feature comparison and API examples
- **FIXES_APPLIED.md** - Bug fix history

### Configuration
- **requirements.txt** - Python dependencies (instagrapi)
- **.gitignore** - Excludes: venv/, session.json, *.json, downloads/, .instagram_user
- **session.json** - Auth session (gitignored, sensitive)
- **.instagram_user** - Username cache (gitignored)

## Architecture

### Authentication Flow
1. Check for existing session.json
2. If exists, load and reuse session
3. If not or expired, prompt for credentials
4. If 2FA enabled, prompt for 6-digit code
5. Save session for future use

### Data Extraction
- Posts from Instagram timeline (algorithmic feed)
- Full metadata: user info, engagement, timestamps, media URLs
- Comments with user details and timestamps
- Media files: photos (.jpg), videos (.mp4), albums

### Output Structure
- **JSON files**: `feed_enhanced_YYYYMMDD_HHMMSS.json`
- **Media folder**: `downloads/username_postid.ext`
- **Data format**: Structured JSON with nested objects

## Key Features
- Full 2FA support with session persistence
- Proper nested media URL extraction (image_versions2, video_versions)
- Human-readable timestamp conversion
- Organized media downloads with consistent naming
- Comment retrieval with pagination
- Comprehensive metadata extraction (location, verified status, filters, etc.)

## Important Directories
- `downloads/` - Media files (gitignored)
- `venv/` - Virtual environment (gitignored)
- `.serena/` - Serena MCP cache
- `__pycache__/` - Python cache (gitignored)

## Development Notes
- Follow Python PEP 8 conventions
- Instagram has rate limits - implement delays for large requests
- Session management is critical - never commit session.json
- All scripts handle 2FA automatically
- Use feed_reader_enhanced.py as reference for new features

## Common Operations
- **Archive feed**: `python feed_reader_enhanced.py`
- **Quick check**: `python feed_reader.py`
- **Test auth**: `python login_with_2fa.py`
- **Install deps**: `pip install -r requirements.txt`

## Security Considerations
- session.json contains auth tokens - keep secure
- All sensitive files in .gitignore
- Use environment variables for production credentials
- Respect Instagram's Terms of Service and rate limits
