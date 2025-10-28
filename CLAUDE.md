# IG Focus - Instagram Feed Reader & Media Archiver

## Project Overview

**IG Focus** is a Python-based Instagram feed reader and media archiver that uses the `instagrapi` library to access and download content from your Instagram timeline (people you follow). The project provides tools for archiving feed posts, downloading media, fetching comments, and extracting comprehensive metadata.

## Core Purpose

This project enables users to:
- Access their Instagram feed programmatically
- Archive posts with full metadata
- Download photos, videos, and albums
- Retrieve comments and engagement data
- Work with 2FA-protected accounts seamlessly

## Architecture

### Main Components

1. **feed_reader_enhanced.py** - Full-featured feed reader
   - Functions: `login_user()`, `extract_post_data()`, `get_feed_posts()`, `get_post_comments()`, `download_media()`, `display_post_info()`, `main()`
   - Handles 2FA, media downloads, comment fetching, enhanced metadata extraction
   - Primary recommended tool for comprehensive feed archiving

2. **feed_reader.py** - Basic feed reader
   - Functions: `login_user()`, `get_feed_posts()`, `display_post_info()`, `save_feed_to_json()`, `save_credentials()`, `load_credentials()`, `main()`
   - Simpler, faster version for quick feed checks
   - Good for users who don't need media downloads

3. **login_with_2fa.py** - Authentication utility
   - Functions: `login_with_2fa()`, `main()`
   - Dedicated 2FA authentication handler
   - Creates `session.json` for subsequent logins

4. **simple_example.py** - Minimal example
   - Basic implementation without 2FA support
   - Educational reference for understanding the API

### Technology Stack

- **Language**: Python 3
- **Primary Library**: [instagrapi](https://github.com/subzeroid/instagrapi)
- **Authentication**: Session-based with 2FA support
- **Data Format**: JSON output with timestamps
- **Media Storage**: Local filesystem (`downloads/` folder)

## Key Features

### Authentication & Security
- Full 2FA (two-factor authentication) support
- Session reuse (no repeated logins)
- Secure credential storage in `session.json`
- Automatic 2FA code prompt when needed

### Data Extraction
- **Post Information**: ID, code, URL, caption, media type
- **User Details**: Username, full name, user ID, verified status
- **Engagement**: Like counts, comment counts, actual comments
- **Media**: Thumbnail URLs, video URLs, proper nested data extraction
- **Metadata**: Location, filters, paid partnerships, audio presence
- **Timestamps**: Both Unix and human-readable formats

### Media Downloads
- Photos (.jpg)
- Videos (.mp4)
- Albums (carousel posts - all items)
- Organized in `downloads/` with `username_postid` naming

### Output Formats
- Timestamped JSON files: `feed_enhanced_YYYYMMDD_HHMMSS.json`
- Downloaded media with consistent naming
- Structured data for easy parsing and analysis

## Development Guidelines

### Code Style
- Follow Python PEP 8 conventions
- Use descriptive function names
- Comment complex logic and API interactions
- Handle errors gracefully with try-except blocks

### Session Management
- Always check for existing `session.json` before creating new sessions
- Implement automatic session renewal on expiration
- Never commit `session.json` to version control

### Rate Limiting Considerations
- Instagram API has rate limits
- Add delays between large batch requests
- Implement exponential backoff for failed requests
- Limit concurrent downloads to avoid throttling

### Testing Workflow
1. Test authentication with `login_with_2fa.py`
2. Verify basic functionality with `feed_reader.py`
3. Test enhanced features with `feed_reader_enhanced.py`
4. Check downloaded media integrity
5. Validate JSON output structure

## Common Use Cases

### 1. Feed Archiving
```bash
python feed_reader_enhanced.py
# Select: fetch comments + download media
```

### 2. Quick Feed Check
```bash
python feed_reader.py
# Fast, no downloads
```

### 3. Initial Setup / 2FA Testing
```bash
python login_with_2fa.py
# Creates session.json for future use
```

### 4. Chronological Sorting
Since Instagram's feed is algorithmic, sort the JSON output by timestamp:
```python
import json
data = json.load(open('feed.json'))
sorted_posts = sorted(data['posts'], key=lambda x: x['timestamp'])
```

## Security Best Practices

1. **Never commit sensitive files**:
   - `session.json` (contains auth data)
   - `.instagram_user` (stores username)
   - Any `.json` feed outputs (may contain personal data)
   - `.env` files with credentials

2. **Use environment variables** for credentials in production

3. **Implement credential rotation** regularly

4. **Monitor API usage** to avoid account flags

## Known Issues & Solutions

### Issue: "Two-factor authentication required"
**Solution**: All scripts now support 2FA. Enter the 6-digit code when prompted.

### Issue: Null thumbnail/video URLs
**Solution**: Use `feed_reader_enhanced.py` which properly extracts nested media URLs.

### Issue: Rate limiting errors
**Solution**:
- Wait 5-10 minutes between requests
- Reduce post count (`amount` parameter)
- Space out media downloads

### Issue: Session expired
**Solution**:
- Delete `session.json`
- Run script again to create fresh session

## Future Enhancement Ideas

- [ ] Implement database storage (SQLite/PostgreSQL)
- [ ] Add command-line arguments for batch operations
- [ ] Create web dashboard for viewing archived content
- [ ] Add story archiving functionality
- [ ] Implement selective user feed filtering
- [ ] Add notification system for new posts
- [ ] Create export to other formats (CSV, XML)
- [ ] Add media deduplication
- [ ] Implement incremental backups

## File Structure

```
ig/
├── feed_reader_enhanced.py    # Full-featured reader (RECOMMENDED)
├── feed_reader.py             # Basic reader
├── login_with_2fa.py          # 2FA authentication utility
├── simple_example.py          # Minimal example
├── requirements.txt           # Python dependencies
├── README.md                  # User documentation
├── CLAUDE.md                  # This file - project guide
├── FEATURES.md                # Feature details and comparisons
├── FIXES_APPLIED.md           # Bug fix history
├── .gitignore                 # Git exclusions
├── session.json               # Auth session (gitignored)
├── .instagram_user            # Username cache (gitignored)
├── downloads/                 # Downloaded media (gitignored)
└── venv/                      # Virtual environment (gitignored)
```

## API Capabilities Reference

The `instagrapi` library provides extensive functionality beyond this project's current scope:

- User information retrieval
- Follower/following lists
- Direct messaging
- Story access and download
- Post interactions (like, comment)
- Hashtag and user search
- Media upload
- Profile editing

See [instagrapi documentation](https://subzeroid.github.io/instagrapi/) for complete API reference.

## Contributing Guidelines

When adding features:
1. Maintain backward compatibility with existing scripts
2. Update documentation (README.md, CLAUDE.md, FEATURES.md)
3. Test with 2FA-enabled accounts
4. Verify rate limiting doesn't trigger bans
5. Add proper error handling
6. Update Serena memories if architecture changes

## Performance Notes

- **Basic feed fetch**: ~2-3 seconds for 20 posts
- **With comments**: ~1 second per post overhead
- **With downloads**: Variable, depends on media sizes
- **Storage**: ~50KB JSON (20 posts), ~5-50MB per post with media

## Git Workflow

- Work on `develop` branch for features
- Commit after completing significant tasks
- Use descriptive commit messages
- Push to GitHub after each complete feature
- Never commit sensitive files (see .gitignore)

## Version Control

Current state:
- **Not yet initialized** - Git repo to be created
- **GitHub repo name**: `IG Focus`
- **Branch strategy**: `main` for releases, `develop` for active work
- **Exclusions**: downloads/, session.json, .instagram_user, *.json outputs

## Project Maintenance

- Regularly update `instagrapi` library for API compatibility
- Monitor Instagram API changes and deprecations
- Update documentation when features are added
- Clean up old JSON outputs periodically
- Audit downloaded media storage space
- Review and update rate limiting thresholds

## Contact & Support

For issues with:
- **Instagram API**: Check [instagrapi issues](https://github.com/subzeroid/instagrapi/issues)
- **Project bugs**: Create issue in project repository
- **Feature requests**: Document in project issues with enhancement label

---

**Last Updated**: October 2024
**Python Version**: 3.7+
**Primary Dependency**: instagrapi
**License**: MIT (via instagrapi)
