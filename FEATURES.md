# Instagram Feed Reader - Features & Answers

## Answers to Your Questions

### 1. **Can we download media (images/videos)?**
✅ **YES!** The enhanced script (`feed_reader_enhanced.py`) can download:
- Photos (.jpg)
- Videos (.mp4)
- Albums (all items in carousel posts)

Files are saved to a `downloads/` folder with naming: `username_postid.jpg`

### 2. **Can we get comments?**
✅ **YES!** The enhanced script can fetch comments including:
- Username
- Comment text
- Timestamp
- Number of likes on the comment

You can specify `max_comments` per post (default: 50)

### 3. **Is the feed chronological or algorithmic?**
⚠️ **ALGORITHMIC** - Instagram's `get_timeline_feed()` returns the same feed you see in the app, which is algorithmically sorted.

**To get chronological:**
Unfortunately, Instagram removed true chronological feeds from their API. However, you can:
- Sort the saved JSON by timestamp afterwards
- Use `cl.user_medias(user_id, amount=X)` to get a specific user's posts chronologically
- Request "Following" feed sorting in the Instagram app settings (though API still uses algorithm)

### 4. **Human-readable timestamps?**
✅ **FIXED!** The enhanced script now includes:
- `timestamp`: Unix timestamp (original)
- `timestamp_human`: "2024-10-19 14:30:52" format

### 5. **Why are thumbnail_url and video_url null?**
🔧 **FIXED!** The issue was:
- Basic extraction wasn't diving into nested `image_versions2` and `video_versions`
- The enhanced script properly extracts:
  - `image_versions2.candidates[0].url` for photos
  - `video_versions[0].url` for videos

### 6. **What other data can we get?**

The enhanced script now extracts:

#### **Basic Info**
- `id` - Post ID
- `code` - Short code for URL
- `url` - Direct Instagram link

#### **User Info**
- `user` - Username
- `user_id` - User ID
- `user_full_name` - Display name
- `is_verified` - Verified badge

#### **Content**
- `caption` - Full caption text
- `media_type` - Type code (1/2/8)
- `media_type_name` - "photo"/"video"/"album"
- `carousel_media_count` - Items in album

#### **Engagement**
- `likes` - Like count
- `comments_count` - Comment count
- `comments` - Array of comment objects (if fetched)

#### **Media URLs**
- `thumbnail_url` - Image URL
- `video_url` - Video URL
- `downloaded_files` - Local file paths (if downloaded)

#### **Metadata**
- `location` - Location name
- `filter_type` - Applied filter
- `is_paid_partnership` - Sponsored content
- `can_save` - Can viewer save
- `has_audio` - Has audio track

#### **Timestamps**
- `timestamp` - Unix timestamp
- `timestamp_human` - Readable format

## Using the Enhanced Script

```bash
python feed_reader_enhanced.py
```

### Options:
1. **How many posts?** - Set amount (default: 20)
2. **Fetch comments?** - Get comments for each post
3. **Download media?** - Save images/videos locally

### Output:
- JSON file: `feed_enhanced_YYYYMMDD_HHMMSS.json` with all metadata
- Downloads folder: `downloads/` with media files (if enabled)

## Additional Features

### Media Download Methods

```python
# Download single photo
cl.photo_download_by_url(url, filepath)

# Download video
cl.video_download_by_url(url, filepath)

# Get full media info (for albums)
media_info = cl.media_info(media_pk)
```

### Getting Chronological Posts from Specific Users

```python
# Get user ID
user_id = cl.user_id_from_username("username")

# Get their posts chronologically
posts = cl.user_medias(user_id, amount=50)
```

### Fetching More Comments

```python
# Get more comments
comments = cl.media_comments(post_id, amount=100)
```

### Other Available Methods

```python
# Get user info
user_info = cl.user_info(user_id)

# Get followers
followers = cl.user_followers(user_id, amount=100)

# Get following
following = cl.user_following(user_id, amount=100)

# Like a post
cl.media_like(media_id)

# Comment on post
cl.media_comment(media_id, "Great post!")

# Get stories
stories = cl.user_stories(user_id)

# Download story
cl.story_download(story_pk)
```

## Comparison: Basic vs Enhanced

| Feature | feed_reader.py | feed_reader_enhanced.py |
|---------|----------------|-------------------------|
| Session reuse | ✅ | ✅ |
| Human timestamps | ❌ | ✅ |
| Proper URLs | ❌ | ✅ |
| Download media | ❌ | ✅ |
| Fetch comments | ❌ | ✅ |
| Full metadata | ❌ | ✅ |
| User full names | ❌ | ✅ |
| Location data | ❌ | ✅ |
| Verified badges | ❌ | ✅ |
| Album handling | ❌ | ✅ |

## Performance Notes

- **Without downloads**: Very fast (~2-3 seconds for 20 posts)
- **With comments**: Slower (~1 second per post)
- **With media downloads**: Much slower (depends on file sizes)

## Rate Limiting

Instagram limits API requests. If you get rate limited:
- Wait 5-10 minutes
- Reduce number of posts fetched
- Don't fetch comments/media for every post
- Space out your requests

## Storage

Example file sizes:
- JSON only: ~50KB per 20 posts
- With comments: ~200KB per 20 posts
- With media: ~5-50MB per post (varies by media type)
