# IG Focus - Instagram Feed Reader & Media Archiver

A Python-based tool to access, archive, and download content from your Instagram feed using [instagrapi](https://github.com/subzeroid/instagrapi).

## Features

### Archive & Download
- Full 2FA (two-factor authentication) support
- Session reuse - no repeated logins
- Download photos, videos, and albums
- Fetch post comments and engagement data
- Extract comprehensive metadata
- Human-readable timestamps
- Organized JSON output with timestamps

### Web Viewer 🎨 NEW!
- Beautiful Instagram-like web interface
- View downloaded feeds offline in your browser
- No server required - pure HTML/CSS/JavaScript
- Fully accessible with keyboard navigation
- Filter by type, search by content
- Lightbox for full-size media viewing
- See [viewer/README.md](viewer/README.md) for details

## Setup

1. **Create and activate virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **First-time authentication:**
   ```bash
   python login_with_2fa.py
   ```
   Enter your 6-digit 2FA code when prompted. This creates a `session.json` file for future logins.

## Quick Start

### 1. Download Your Feed

```bash
python feed_reader_enhanced.py
```

### 2. View Your Feed

Open `viewer/index.html` in your browser to view your downloaded feed in a beautiful, Instagram-like interface.

For best results with local media files:
```bash
# Run from the ig/ directory
python3 -m http.server 8000
# Then open: http://localhost:8000/viewer/
```

## Usage Options

### Option 1: Enhanced Feed Reader (RECOMMENDED) ✅ All Features

Run the fully-featured enhanced script:

```bash
python feed_reader_enhanced.py
```

Features:
- ✅ **Full 2FA support** & session reuse (no repeated logins!)
- ✅ **Download media** - Photos, videos, and albums
- ✅ **Fetch comments** - Get all comments on posts
- ✅ **Human-readable timestamps** - Formatted dates
- ✅ **Proper media URLs** - Fixed thumbnail/video extraction
- ✅ **Extended metadata** - Location, verified badges, full names, etc.
- Auto-saves to timestamped JSON files

**Perfect for:** Archiving your feed, downloading content, analyzing engagement

### Option 2: Basic Feed Reader ✅ 2FA Support

Run the simpler version:

```bash
python feed_reader.py
```

Features:
- ✅ **Full 2FA support** & session reuse
- Fetches and displays posts
- Auto-saves to JSON
- Faster (no downloads or comments)

**Perfect for:** Quick feed checks without downloads

### Option 3: Test Login with 2FA ✅ 2FA Support

First-time setup or testing your credentials:

```bash
python login_with_2fa.py
```

This script:
- Handles 2FA authentication
- Saves your session for future use
- Shows your account info on successful login
- Creates `session.json` for subsequent logins

### Option 4: Simple Example (No 2FA)

Edit `simple_example.py` and replace the credentials:

```python
username = "your_username"
password = "your_password"
```

Then run:

```bash
python simple_example.py
```

⚠️ **Note:** This script doesn't support 2FA. Use Option 1 or 2 if you have 2FA enabled.

## What You Can Access

The scripts retrieve posts from your Instagram feed (timeline) including:

- **Post Information:**
  - Post ID
  - Username of poster
  - Caption text
  - Like count
  - Comment count
  - Post timestamp
  - Media type (photo, video, album)

- **Media URLs:**
  - Thumbnail URLs
  - Video URLs (if applicable)

## Output

### JSON Files
Each run creates a timestamped JSON file:
- Format: `feed_enhanced_YYYYMMDD_HHMMSS.json`
- Contains: All post metadata, comments, URLs, timestamps
- Location: Project root directory

### Downloaded Media
If media download is enabled:
- Location: `downloads/` folder
- Naming: `username_postid.jpg` or `username_postid.mp4`
- Organized by post for easy reference

## Security Notes

� **Important:**
- Never commit your credentials to version control
- The `session.json` file contains sensitive login data - keep it secure
- Consider using environment variables for credentials in production

## API Capabilities

Using instagrapi, you can also:
- Get user information
- Download photos and videos
- Like/unlike posts
- Comment on posts
- Get followers/following lists
- Search for users and hashtags
- Access stories
- And much more!

See the [instagrapi documentation](https://subzeroid.github.io/instagrapi/) for full API reference.

## Two-Factor Authentication (2FA)

If your account has 2FA enabled (recommended for security), the scripts will:

1. Detect that 2FA is required
2. Prompt you to enter the 6-digit verification code
3. Accept the code from your:
   - Authentication app (Google Authenticator, Authy, etc.)
   - SMS message
   - Email

**First Login with 2FA:**
```bash
python login_with_2fa.py
# or
python feed_reader.py
```

When prompted, enter the 6-digit code from your authenticator app.

**Subsequent Logins:**
Once you've logged in successfully, a `session.json` file is created. Future logins will:
- Use the saved session (no 2FA needed)
- Only ask for 2FA if the session expires

## Troubleshooting

**"Two-factor authentication required" Error:**
- ✅ **Solution:** Scripts now support 2FA! Just run them and enter your verification code when prompted.
- The code will be sent to your authentication app or phone
- Enter the 6-digit code when asked

**Login Issues:**
- Make sure you're entering the correct username (not email)
- Check that your password is correct
- If session is corrupted, delete `session.json` and login fresh
- Instagram may temporarily block login attempts if you try too many times

**Rate Limiting:**
- Instagram limits API requests
- Wait a few minutes between large requests
- Don't fetch too many posts at once

**Session Expired:**
- If you see errors about expired sessions, delete `session.json`
- Run the script again to create a fresh session

## Project Structure

```
ig/
├── feed_reader_enhanced.py    # Full-featured reader (RECOMMENDED)
├── login_with_2fa.py          # 2FA authentication utility
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── CLAUDE.md                  # Developer guide
├── FEATURES.md                # Detailed feature comparison
├── viewer/                    # Web viewer for viewing feeds
│   ├── index.html            # Main viewer page
│   ├── styles.css            # Instagram-like styling
│   ├── script.js             # Feed display logic
│   └── README.md             # Viewer documentation
├── downloads/                 # Downloaded media (created on first use)
└── archive/                   # Archived old scripts
```

## Additional Documentation

- **[CLAUDE.md](CLAUDE.md)** - Comprehensive developer guide, architecture details, and best practices
- **[FEATURES.md](FEATURES.md)** - Detailed feature comparison and API examples
- **[FIXES_APPLIED.md](FIXES_APPLIED.md)** - Bug fix history

## Contributing

This is a personal project, but suggestions are welcome! Please:
1. Check existing issues first
2. Follow the code style in existing files
3. Test with 2FA-enabled accounts
4. Update documentation for new features

## License

This project uses instagrapi which is licensed under MIT.

## Disclaimer

This tool is for personal use to access your own Instagram feed. Please respect Instagram's Terms of Service and rate limits. Do not use this tool for spam, harassment, or any malicious purposes.
