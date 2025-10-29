# IG Focus Web Viewer

A beautiful, accessible, Instagram-like web viewer for your downloaded Instagram feed data. View your archived posts offline with photos, videos, captions, and comments.

## Features

✨ **Instagram-Inspired Design**
- Clean, modern interface similar to Instagram
- Responsive grid layout
- Smooth animations and transitions

🎯 **Fully Accessible**
- Keyboard navigation support
- Screen reader friendly
- High contrast mode support
- Focus indicators
- ARIA labels

📱 **Responsive**
- Works on desktop, tablet, and mobile
- Adapts to different screen sizes
- Touch-friendly controls

🔍 **Powerful Filtering**
- Filter by media type (photos, videos, albums)
- Search by username, caption, or full name
- Real-time filtering

🖼️ **Media Viewing**
- Click any post to open in lightbox
- View photos and videos in full size
- Navigate with arrow keys or buttons
- Supports local downloaded media files
- Fallback to URLs if local files not available

## How to Use

### 1. Open the Viewer

Simply open `index.html` in your web browser:
- Double-click the file, or
- Right-click and choose "Open with" → your browser, or
- Drag the file into your browser window

**Note:** For best results with local media files, use a local web server (see below).

### 2. Load Your Feed

1. Click the **"📂 Load Feed JSON"** button
2. Select your feed JSON file (e.g., `feed_enhanced_20251029_063308.json`)
3. Your posts will appear instantly!

### 3. Browse Your Feed

- **Scroll** through your posts in a grid layout
- **Click** any post to view it full-size in the lightbox
- **Filter** by type using the dropdown
- **Search** for specific users or content
- **Navigate** the lightbox with arrow keys (← →) or on-screen buttons
- **Close** lightbox with X button or ESC key

## Viewing Local Media Files

The viewer can display downloaded media files from your `downloads/` folder. However, browsers have security restrictions on loading local files.

### Option 1: Simple (URLs Only)
Just open `index.html` in your browser. The viewer will display:
- Online URLs from Instagram (if available in JSON)
- Limited local file support depending on browser

### Option 2: Local Web Server (Recommended)
For full local media support, run a simple web server:

**Using Python 3:**
```bash
# From the ig/ directory (parent of viewer/)
python3 -m http.server 8000
```

Then open: `http://localhost:8000/viewer/`

**Using Node.js:**
```bash
# Install if needed
npm install -g http-server

# From the ig/ directory
http-server -p 8000
```

Then open: `http://localhost:8000/viewer/`

**Why use a server?**
- Loads local images/videos from `downloads/` folder
- No CORS or file:// protocol restrictions
- Full functionality

## File Structure

```
ig/
├── viewer/
│   ├── index.html          # Main viewer page
│   ├── styles.css          # Instagram-like styling
│   ├── script.js           # Feed loading and display logic
│   └── README.md           # This file
├── downloads/              # Your downloaded media files
│   ├── username_postid.jpg
│   ├── username_postid.mp4
│   └── ...
└── feed_enhanced_*.json    # Your feed data files
```

## Keyboard Shortcuts

- **ESC** - Close lightbox
- **← Left Arrow** - Previous post in lightbox
- **→ Right Arrow** - Next post in lightbox
- **Enter/Space** - Open post (when focused)
- **Tab** - Navigate between elements

## Accessibility Features

- ✅ Full keyboard navigation
- ✅ Screen reader support with ARIA labels
- ✅ Focus indicators for keyboard users
- ✅ High contrast mode support
- ✅ Reduced motion support
- ✅ Alt text for all images
- ✅ Semantic HTML structure

## Browser Compatibility

Works in all modern browsers:
- ✅ Chrome/Edge (recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Opera

**Note:** Internet Explorer is not supported.

## Features by Post Type

### Photos
- Thumbnail in grid view
- Full-size in lightbox
- Supports local files and URLs

### Videos
- Thumbnail with play icon
- Full video player in lightbox with controls
- Auto-play in lightbox

### Albums
- Shows first image
- Indicator showing number of items
- Lightbox shows first item (full album browsing coming soon)

## Data Display

For each post, you'll see:
- **User Info**: Username, full name, verified badge
- **Timestamp**: Human-readable date and time
- **Media**: Photo, video, or album preview
- **Stats**: Likes and comment counts
- **Caption**: Full caption text
- **Location**: If available
- **Comments**: First 3 comments with "show more" indicator
- **Sponsored**: Badge for sponsored content
- **Link**: Direct link to original Instagram post

## Privacy & Security

- ✅ **100% Client-side**: All processing happens in your browser
- ✅ **No Data Sent**: Nothing is uploaded or sent anywhere
- ✅ **Offline Capable**: Works without internet (with local server)
- ✅ **Your Data Only**: Only reads files you explicitly select

## Troubleshooting

### Images Not Loading
1. Make sure you're using a local web server (see above)
2. Check that `downloads/` folder is in the parent directory of `viewer/`
3. Verify image filenames match those in the JSON file
4. The viewer will automatically fall back to Instagram URLs if local files fail

### Avatar Images Not Showing
- **This is normal!** Instagram's CDN blocks loading profile pictures from external websites (CORS policy)
- The viewer automatically falls back to showing the first letter of the username in a colored circle
- This is a security feature by Instagram and cannot be bypassed in the browser
- Downloaded media (posts) will work fine, only external avatar URLs are blocked

### JSON Parse Error
- Make sure you selected a valid JSON file
- Check that the file isn't corrupted
- Try re-downloading your feed

### Filters Not Working
- Clear your search text
- Reset filter to "All Posts"
- Reload the page and try again

### Lightbox Issues
- Press ESC to close
- Refresh the page if buttons aren't responding
- Make sure JavaScript is enabled

## Future Enhancements

Planned features:
- [ ] Full album carousel in lightbox
- [ ] Export filtered results
- [ ] Dark mode toggle
- [ ] Comparison view (multiple feeds)
- [ ] Statistics dashboard
- [ ] Download all media button
- [ ] Timeline view

## Technical Details

- **Pure HTML/CSS/JavaScript** - No frameworks or dependencies
- **Responsive Grid** - CSS Grid with auto-fill
- **Accessible** - WCAG 2.1 AA compliant
- **Performance** - Lazy loading and efficient rendering
- **Modern Standards** - Uses ES6+ JavaScript features

## Contributing

Have ideas for improvements? Found a bug? This viewer is part of the IG Focus project. Check the main repository for contribution guidelines.

## License

Part of IG Focus project. See main project README for license information.

---

**Enjoy viewing your Instagram archive! 📸**
