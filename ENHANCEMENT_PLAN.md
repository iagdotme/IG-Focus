# IG Focus Enhancement Plan
## Feed Reader Enhanced v2.0

**Goal**: Create a robust, production-ready Instagram feed archiver with proper pagination, optional media/comment downloads, and best practices implementation.

---

## 🎯 Core Objectives

1. **Fix Critical Pagination Bug** - Implement proper `get_timeline_feed()` pagination
2. **Optimize API Usage** - Reduce unnecessary calls, implement proper rate limiting
3. **Improve User Experience** - Better progress reporting, resumable downloads
4. **Add Flexibility** - Command-line arguments for automation
5. **Enhance Reliability** - Better error handling, retry logic, session management

---

## 📋 Detailed Enhancement Roadmap

### Phase 1: Fix Pagination (CRITICAL - Current Implementation Broken)

**Problem**: Current implementation doesn't use pagination correctly
- Missing `reason` parameter
- Not extracting `next_max_id` from responses
- Not passing `max_id` to subsequent calls
- Results in duplicate/incomplete data

**Solution**:
```python
def get_feed_posts(cl: Client, amount: int = 20) -> list:
    """Get feed posts with PROPER pagination"""
    all_posts = []
    max_id = None
    max_pages = 20  # Safety limit

    for page in range(max_pages):
        # Use correct reason parameter
        if max_id:
            timeline = cl.get_timeline_feed(
                reason="pagination",
                max_id=max_id
            )
        else:
            timeline = cl.get_timeline_feed(
                reason="cold_start_fetch"
            )

        # Extract feed items
        feed_items = timeline.get('feed_items', [])
        if not feed_items:
            break

        posts = [
            item['media_or_ad']
            for item in feed_items
            if 'media_or_ad' in item
        ]

        # Deduplicate by pk
        existing_pks = {
            getattr(p, 'pk', p.get('pk'))
            for p in all_posts
        }
        new_posts = [
            p for p in posts
            if getattr(p, 'pk', p.get('pk')) not in existing_pks
        ]

        if not new_posts:
            break

        all_posts.extend(new_posts)

        if len(all_posts) >= amount:
            break

        # Get next page cursor (CRITICAL!)
        max_id = timeline.get('next_max_id')
        if not max_id:
            break

        # Rate limiting delay
        time.sleep(random.uniform(2, 4))

    return all_posts[:amount]
```

**Benefits**:
- Actually fetches requested number of posts
- No duplicates
- Respects API pagination properly
- Follows Instagram best practices

---

### Phase 2: Improve Session Management

**Current Issues**:
- Session validation happens on every startup (unnecessary API call)
- No session expiry detection
- Password required even when session is valid

**Enhancements**:

1. **Lazy Session Validation**
   - Don't validate until first actual API call
   - Remove `cl.get_timeline_feed()` validation check in login

2. **Session Expiry Detection**
   - Catch specific exceptions indicating expired session
   - Auto-prompt for re-login only when needed

3. **Better Session Reuse**
   ```python
   def login_user(username: str, password: str = None, session_file: str = "session.json") -> Client:
       cl = Client()
       cl.delay_range = [1, 3]
       cl.request_timeout = 30

       session_path = Path(session_file)

       # Try session first (no validation)
       if session_path.exists():
           try:
               cl.load_settings(session_path)
               # Don't validate here - wait for first API call
               return cl
           except Exception:
               pass

       # Fresh login only if session load failed
       if not password:
           password = getpass.getpass("Password: ")

       try:
           cl.login(username, password)
       except TwoFactorRequired:
           code = input("2FA code: ").strip()
           cl.login(username, password, verification_code=code)

       cl.dump_settings(session_path)
       return cl
   ```

---

### Phase 3: Enhanced Download Features

**Current State**: Media download works but lacks features

**Improvements**:

1. **Skip Already Downloaded Media**
   ```python
   def get_downloaded_post_ids(download_dir: str) -> set:
       """Get list of already downloaded post IDs from filenames"""
       files = Path(download_dir).glob("*")
       post_ids = set()
       for f in files:
           # Extract post_id from filename: username_postid_*.ext
           parts = f.stem.split('_')
           if len(parts) >= 2:
               post_ids.add(parts[1])
       return post_ids

   # In main():
   already_downloaded = get_downloaded_post_ids(download_dir)
   if post_id in already_downloaded and not force_redownload:
       print(f"  ⏭ Already downloaded")
       continue
   ```

2. **Progress Bars for Downloads**
   - Add `tqdm` library for progress bars
   - Show download speed and ETA

3. **Parallel Downloads** (optional, advanced)
   - Use `ThreadPoolExecutor` for concurrent downloads
   - Limit to 3-5 concurrent connections to avoid rate limits

4. **Better File Organization**
   ```
   downloads/
   ├── 2025-01-15/
   │   ├── username_postid_1.jpg
   │   ├── username_postid_2.mp4
   ├── 2025-01-14/
   │   └── ...
   ```

5. **Media Quality Options**
   - Add option to download highest quality available
   - Option to download thumbnails only (space saving)

---

### Phase 4: Comment Fetching Enhancements

**Current State**: Basic comment fetching works

**Improvements**:

1. **Configurable Comment Depth**
   - Option to fetch all comments (not just first 50)
   - Option to fetch comment replies

2. **Comment Metadata**
   - User verification status
   - Comment likes
   - Reply count
   - Timestamps

3. **Rate Limiting for Comments**
   - Add delays between comment fetches
   - Batch comment requests

---

### Phase 5: Add Command-Line Arguments

**Enable Automation & Scripting**

```python
import argparse

def parse_args():
    parser = argparse.ArgumentParser(
        description='Instagram Feed Reader & Archiver'
    )

    # Login
    parser.add_argument('-u', '--username', help='Instagram username')
    parser.add_argument('-p', '--password', help='Instagram password')
    parser.add_argument('--session', default='session.json', help='Session file')

    # Fetching
    parser.add_argument('-n', '--amount', type=int, default=20,
                       help='Number of posts to fetch')
    parser.add_argument('--skip-sponsored', action='store_true',
                       help='Skip sponsored posts')
    parser.add_argument('--chronological', action='store_true',
                       help='Sort chronologically')

    # Optional features
    parser.add_argument('--download-media', action='store_true',
                       help='Download photos/videos')
    parser.add_argument('--fetch-comments', action='store_true',
                       help='Fetch comments')
    parser.add_argument('--max-comments', type=int, default=50,
                       help='Max comments per post')

    # Output
    parser.add_argument('-o', '--output', help='Output JSON filename')
    parser.add_argument('--download-dir', default='downloads',
                       help='Directory for media downloads')

    # Advanced
    parser.add_argument('--force-redownload', action='store_true',
                       help='Re-download existing files')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without doing it')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')

    return parser.parse_args()
```

**Benefits**:
- Scriptable/automatable
- CI/CD integration possible
- Cron job friendly
- Easier testing

**Example Usage**:
```bash
# Basic: Fetch 20 posts, no downloads
python feed_reader_enhanced.py -u myusername -n 20

# Full archive: Download everything
python feed_reader_enhanced.py -u myusername -n 100 \
    --download-media --fetch-comments --chronological

# Quick check: See latest posts without downloading
python feed_reader_enhanced.py -n 10

# Automation: Daily backup
python feed_reader_enhanced.py -n 50 --download-media \
    --skip-sponsored -o "backup_$(date +%Y%m%d).json"
```

---

### Phase 6: Better Error Handling & Recovery

**Improvements**:

1. **Specific Exception Handling**
   ```python
   from instagrapi.exceptions import (
       LoginRequired,
       PleaseWaitFewMinutes,
       RateLimitError,
       MediaNotFound,
       ClientError
   )

   def safe_api_call(func, *args, max_retries=3, **kwargs):
       """Wrapper for API calls with retry logic"""
       for attempt in range(max_retries):
           try:
               return func(*args, **kwargs)
           except PleaseWaitFewMinutes:
               wait_time = 60 * (attempt + 1)
               print(f"⏳ Rate limited. Waiting {wait_time}s...")
               time.sleep(wait_time)
           except RateLimitError:
               wait_time = 300  # 5 minutes
               print(f"🚫 Rate limit hit. Waiting {wait_time}s...")
               time.sleep(wait_time)
           except ClientError as e:
               if attempt < max_retries - 1:
                   print(f"⚠ Error: {e}. Retrying...")
                   time.sleep(5)
               else:
                   raise
       raise Exception(f"Failed after {max_retries} attempts")
   ```

2. **Checkpoint/Resume Functionality**
   - Save progress periodically
   - Resume from last checkpoint on failure
   - Save partial results even if script crashes

3. **Better Logging**
   ```python
   import logging

   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(levelname)s - %(message)s',
       handlers=[
           logging.FileHandler('ig_focus.log'),
           logging.StreamHandler()
       ]
   )
   ```

---

### Phase 7: Data Persistence & Deduplication

**Problem**: Multiple runs create duplicate JSON files with overlapping data

**Solutions**:

1. **SQLite Database Backend** (optional)
   - Store posts in database
   - Automatic deduplication
   - Easy querying
   - Track download status

2. **Smart JSON Merging**
   ```python
   def merge_with_existing_data(new_posts: list, existing_file: str) -> list:
       """Merge new posts with existing JSON, avoid duplicates"""
       if Path(existing_file).exists():
           with open(existing_file) as f:
               existing = json.load(f)

           existing_ids = {p['id'] for p in existing}
           new_posts = [p for p in new_posts if p['id'] not in existing_ids]

           return existing + new_posts
       return new_posts
   ```

3. **Archive Mode**
   - Maintain single `feed_archive.json` with all posts
   - Update incrementally
   - Add `--archive` flag

---

### Phase 8: Additional Features

**Nice-to-Have Enhancements**:

1. **Filter Options**
   - Filter by date range
   - Filter by user
   - Filter by media type (photos only, videos only)
   - Filter by engagement (min likes/comments)

2. **Export Formats**
   - CSV export
   - HTML viewer
   - Markdown summary

3. **Statistics & Analytics**
   ```python
   def generate_stats(posts: list) -> dict:
       return {
           'total_posts': len(posts),
           'total_likes': sum(p['likes'] for p in posts),
           'total_comments': sum(p['comments_count'] for p in posts),
           'media_types': Counter(p['media_type_name'] for p in posts),
           'top_users': Counter(p['user'] for p in posts).most_common(10),
           'sponsored_count': sum(p['is_sponsored'] for p in posts),
           'date_range': (min(p['timestamp'] for p in posts),
                         max(p['timestamp'] for p in posts))
       }
   ```

4. **Incremental Backup Mode**
   - `--since-last-run` flag
   - Only fetch posts newer than last run
   - Store last run timestamp

---

## 🔧 Implementation Order (Priority)

### Week 1: Critical Fixes
1. ✅ **Fix pagination** (Phase 1) - HIGHEST PRIORITY
2. ✅ Improve session management (Phase 2)
3. ✅ Add basic CLI arguments (Phase 5 - partial)

### Week 2: Feature Enhancements
4. ✅ Enhanced downloads (Phase 3)
5. ✅ Better error handling (Phase 6)
6. ✅ Comment improvements (Phase 4)

### Week 3: Polish & Advanced
7. ✅ Data persistence (Phase 7)
8. ✅ Additional features (Phase 8)
9. ✅ Documentation updates
10. ✅ Testing & validation

---

## 📊 Success Metrics

**How we'll know it's working**:

- ✅ Pagination: Can fetch 100+ posts reliably without duplicates
- ✅ Performance: No unnecessary API calls (check logs)
- ✅ Reliability: Handles rate limits gracefully
- ✅ Usability: Can run unattended via cron
- ✅ Data Quality: All media downloads succeed, all metadata captured

---

## 🧪 Testing Plan

1. **Unit Tests**
   - Test pagination logic
   - Test deduplication
   - Test data extraction

2. **Integration Tests**
   - Test full download cycle
   - Test session reuse
   - Test error recovery

3. **Manual Tests**
   - Fetch 100 posts with all options
   - Verify no duplicates
   - Check download integrity
   - Test resume functionality

---

## 📚 Documentation Updates Needed

After implementation:

1. Update `CLAUDE.md` with new architecture
2. Update `README.md` with new features and usage
3. Update `FEATURES.md` with comparisons
4. Create `USAGE.md` with CLI examples
5. Add inline code documentation
6. Create troubleshooting guide

---

## 🚀 Quick Start (After Implementation)

```bash
# Install dependencies
pip install -r requirements.txt

# Basic usage (interactive)
python feed_reader_enhanced.py

# Automated daily backup
python feed_reader_enhanced.py \
    -u myusername \
    -n 50 \
    --download-media \
    --fetch-comments \
    --chronological \
    --skip-sponsored \
    -o "feed_$(date +%Y%m%d).json"

# Incremental archive mode
python feed_reader_enhanced.py \
    -n 100 \
    --archive \
    --since-last-run
```

---

## 💡 Future Possibilities

- Web UI for browsing archived content
- Story archiving
- Hashtag tracking
- User profile archiving
- Scheduled automated backups
- Cloud storage integration (S3, Google Drive)
- Notification system for new posts from favorite accounts

---

**Last Updated**: January 2025
**Status**: Ready for Implementation
**Estimated Effort**: 3 weeks (if working part-time)
