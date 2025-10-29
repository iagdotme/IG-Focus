// Global state
let feedData = null;
let filteredPosts = [];
let currentLightboxIndex = 0;

// DOM Elements
const feedFileInput = document.getElementById('feed-file-input');
const feedContainer = document.getElementById('feed');
const instructionsDiv = document.getElementById('instructions');
const filtersDiv = document.getElementById('filters');
const postCountSpan = document.getElementById('post-count');
const loadingDiv = document.getElementById('loading');
const errorDiv = document.getElementById('error');
const typeFilter = document.getElementById('type-filter');
const searchFilter = document.getElementById('search-filter');
const lightbox = document.getElementById('lightbox');
const lightboxMedia = document.getElementById('lightbox-media');
const lightboxCaption = document.getElementById('lightbox-caption');

// Event Listeners
feedFileInput.addEventListener('change', handleFileSelect);
typeFilter.addEventListener('change', applyFilters);
searchFilter.addEventListener('input', applyFilters);
document.querySelector('.lightbox-close').addEventListener('click', closeLightbox);
document.querySelector('.lightbox-prev').addEventListener('click', () => navigateLightbox(-1));
document.querySelector('.lightbox-next').addEventListener('click', () => navigateLightbox(1));
document.addEventListener('keydown', handleKeyPress);

// File Selection Handler
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;

    showLoading();

    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            feedData = JSON.parse(e.target.result);
            console.log('Loaded feed data:', Array.isArray(feedData) ? `Array with ${feedData.length} posts` : `Object with keys: ${Object.keys(feedData).join(', ')}`);
            hideLoading();
            displayFeed();
        } catch (error) {
            console.error('Error parsing JSON:', error);
            errorDiv.innerHTML = `<p>❌ Error parsing JSON file: ${error.message}</p><p>Please check the file format.</p>`;
            showError();
        }
    };
    reader.onerror = function() {
        showError();
    };
    reader.readAsText(file);
}

// Display Feed
function displayFeed() {
    if (!feedData) {
        showError();
        return;
    }

    // Handle both formats: array of posts or object with posts property
    let posts = Array.isArray(feedData) ? feedData : feedData.posts;

    if (!posts || !Array.isArray(posts) || posts.length === 0) {
        errorDiv.innerHTML = '<p>❌ No posts found in this feed file.</p>';
        showError();
        return;
    }

    // Hide instructions, show filters
    instructionsDiv.style.display = 'none';
    filtersDiv.style.display = 'flex';

    // Initialize filtered posts
    filteredPosts = posts;
    applyFilters();
}

// Apply Filters
function applyFilters() {
    if (!feedData) return;

    // Handle both formats
    let allPosts = Array.isArray(feedData) ? feedData : feedData.posts;
    if (!allPosts) return;

    const typeValue = typeFilter.value;
    const searchValue = searchFilter.value.toLowerCase().trim();

    filteredPosts = allPosts.filter(post => {
        // Type filter
        const typeMatch = typeValue === 'all' || post.media_type_name === typeValue;

        // Search filter
        const searchMatch = !searchValue ||
            (post.user && post.user.toLowerCase().includes(searchValue)) ||
            (post.caption && post.caption.toLowerCase().includes(searchValue)) ||
            (post.user_full_name && post.user_full_name.toLowerCase().includes(searchValue));

        return typeMatch && searchMatch;
    });

    renderPosts();
}

// Render Posts
function renderPosts() {
    feedContainer.innerHTML = '';

    if (filteredPosts.length === 0) {
        feedContainer.innerHTML = '<div class="error"><p>No posts match your filters.</p></div>';
        postCountSpan.textContent = '0 posts';
        return;
    }

    postCountSpan.textContent = `${filteredPosts.length} post${filteredPosts.length !== 1 ? 's' : ''}`;

    filteredPosts.forEach((post, index) => {
        const postElement = createPostElement(post, index);
        feedContainer.appendChild(postElement);
    });
}

// Create Post Element
function createPostElement(post, index) {
    const article = document.createElement('article');
    article.className = 'post';
    article.setAttribute('role', 'article');
    article.setAttribute('aria-label', `Post by ${post.user}`);

    // Post Header
    const header = document.createElement('div');
    header.className = 'post-header';

    const avatar = document.createElement('div');
    avatar.className = 'post-avatar';

    // Try to load avatar image, fallback to initial
    if (post.user_avatar_url) {
        const avatarImg = document.createElement('img');
        avatarImg.src = post.user_avatar_url;
        avatarImg.alt = `${post.user}'s avatar`;
        avatarImg.style.width = '100%';
        avatarImg.style.height = '100%';
        avatarImg.style.borderRadius = '50%';
        avatarImg.style.objectFit = 'cover';
        avatarImg.onerror = function() {
            // Fallback to initial letter if image fails
            avatar.textContent = post.user ? post.user.charAt(0).toUpperCase() : '?';
            avatar.style.display = 'flex';
        };
        avatar.appendChild(avatarImg);
        avatar.style.background = 'transparent';
    } else {
        avatar.textContent = post.user ? post.user.charAt(0).toUpperCase() : '?';
    }
    avatar.setAttribute('aria-hidden', 'true');

    const userInfo = document.createElement('div');
    userInfo.className = 'post-user-info';

    const username = document.createElement('div');
    username.className = 'post-username';
    username.innerHTML = `
        ${post.user || 'Unknown'}
        ${post.is_verified ? '<span class="verified-badge" aria-label="Verified">✓</span>' : ''}
    `;

    const timestamp = document.createElement('div');
    timestamp.className = 'post-timestamp';
    timestamp.textContent = formatDate(post.timestamp_human) || 'Unknown date';

    userInfo.appendChild(username);
    userInfo.appendChild(timestamp);

    const typeBadge = document.createElement('div');
    typeBadge.className = 'post-type-badge';
    typeBadge.textContent = post.media_type_name || 'Unknown';

    header.appendChild(avatar);
    header.appendChild(userInfo);
    header.appendChild(typeBadge);

    // Post Media
    const mediaContainer = document.createElement('div');
    mediaContainer.className = 'post-media';
    mediaContainer.setAttribute('tabindex', '0');
    mediaContainer.setAttribute('role', 'button');
    mediaContainer.setAttribute('aria-label', 'View media');
    mediaContainer.addEventListener('click', () => openLightbox(index));
    mediaContainer.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            openLightbox(index);
        }
    });

    const mediaElement = createMediaElement(post);
    mediaContainer.appendChild(mediaElement);

    // Album indicator
    if (post.media_type_name === 'album' && post.carousel_media_count) {
        const albumIndicator = document.createElement('div');
        albumIndicator.className = 'album-indicator';
        albumIndicator.textContent = `📷 ${post.carousel_media_count} items`;
        mediaContainer.appendChild(albumIndicator);
    }

    // Video indicator
    if (post.media_type_name === 'video') {
        const videoIndicator = document.createElement('div');
        videoIndicator.className = 'video-indicator';
        videoIndicator.innerHTML = '▶';
        mediaContainer.appendChild(videoIndicator);
    }

    // Post Content
    const content = document.createElement('div');
    content.className = 'post-content';

    // Stats
    const stats = document.createElement('div');
    stats.className = 'post-stats';
    stats.innerHTML = `
        <span aria-label="${post.likes || 0} likes">❤️ ${formatNumber(post.likes || 0)}</span>
        <span aria-label="${post.comments_count || 0} comments">💬 ${formatNumber(post.comments_count || 0)}</span>
        ${post.is_sponsored ? '<span aria-label="Sponsored">💼 Sponsored</span>' : ''}
    `;

    // Caption
    const caption = document.createElement('div');
    caption.className = 'post-caption';
    if (post.caption) {
        caption.innerHTML = `
            <span class="post-caption-user">${post.user}</span>
            <span class="post-caption-text">${escapeHtml(post.caption)}</span>
        `;
    }

    // Location
    if (post.location) {
        const location = document.createElement('div');
        location.className = 'post-location';
        location.innerHTML = `📍 ${escapeHtml(post.location)}`;
        content.appendChild(stats);
        content.appendChild(caption);
        content.appendChild(location);
    } else {
        content.appendChild(stats);
        content.appendChild(caption);
    }

    // Link to Instagram
    if (post.url) {
        const link = document.createElement('a');
        link.className = 'post-link';
        link.href = post.url;
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        link.textContent = 'View on Instagram →';
        content.appendChild(link);
    }

    // Comments
    if (post.comments && post.comments.length > 0) {
        const commentsContainer = document.createElement('div');
        commentsContainer.className = 'post-comments';

        const commentsHeader = document.createElement('div');
        commentsHeader.className = 'comments-header';
        commentsHeader.textContent = `Comments (${post.comments.length})`;

        commentsContainer.appendChild(commentsHeader);

        // Show first 3 comments
        post.comments.slice(0, 3).forEach(comment => {
            const commentDiv = document.createElement('div');
            commentDiv.className = 'comment';
            commentDiv.innerHTML = `
                <span class="comment-user">${escapeHtml(comment.user || 'Unknown')}</span>
                <span class="comment-text">${escapeHtml(comment.text || '')}</span>
            `;
            commentsContainer.appendChild(commentDiv);
        });

        if (post.comments.length > 3) {
            const moreComments = document.createElement('div');
            moreComments.className = 'comment';
            moreComments.style.color = 'var(--ig-gray)';
            moreComments.textContent = `... and ${post.comments.length - 3} more comments`;
            commentsContainer.appendChild(moreComments);
        }

        content.appendChild(commentsContainer);
    }

    // Assemble post
    article.appendChild(header);
    article.appendChild(mediaContainer);
    article.appendChild(content);

    return article;
}

// Create Media Element
function createMediaElement(post) {
    let element;

    if (post.media_type_name === 'video' && post.video_url) {
        element = document.createElement('video');
        element.controls = false; // Will play in lightbox
        element.preload = 'metadata';
        element.poster = post.thumbnail_url || '';
        element.setAttribute('aria-label', 'Video post');

        // Try local file first, fallback to URL
        if (post.downloaded_files && post.downloaded_files.length > 0) {
            element.src = getLocalMediaPath(post.downloaded_files[0]);
        } else {
            element.src = post.video_url;
        }
    } else {
        element = document.createElement('img');
        element.alt = post.caption ? post.caption.substring(0, 100) : 'Instagram post';

        // Try local file first, fallback to URL
        if (post.downloaded_files && post.downloaded_files.length > 0) {
            element.src = getLocalMediaPath(post.downloaded_files[0]);
        } else if (post.thumbnail_url) {
            element.src = post.thumbnail_url;
        } else {
            element.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="400"%3E%3Crect fill="%23ddd" width="400" height="400"/%3E%3Ctext fill="%23999" x="50%25" y="50%25" text-anchor="middle" dominant-baseline="middle"%3ENo Image%3C/text%3E%3C/svg%3E';
        }

        element.onerror = function() {
            // If local file fails, try URL
            if (post.thumbnail_url && !element.src.includes('http')) {
                element.src = post.thumbnail_url;
            }
        };
    }

    return element;
}

// Get Local Media Path
function getLocalMediaPath(downloadedPath) {
    // Convert absolute path to relative path for web viewing
    // Assumes downloaded files are in ../downloads/ relative to viewer
    const filename = downloadedPath.split('/').pop();
    return `../downloads/${filename}`;
}

// Lightbox Functions
function openLightbox(index) {
    currentLightboxIndex = index;
    const post = filteredPosts[index];

    lightbox.style.display = 'flex';
    lightbox.setAttribute('aria-modal', 'true');
    document.body.style.overflow = 'hidden';

    updateLightboxContent(post);
}

function closeLightbox() {
    lightbox.style.display = 'none';
    lightbox.removeAttribute('aria-modal');
    document.body.style.overflow = '';

    // Pause any videos
    const videos = lightboxMedia.querySelectorAll('video');
    videos.forEach(v => v.pause());
}

function navigateLightbox(direction) {
    currentLightboxIndex = (currentLightboxIndex + direction + filteredPosts.length) % filteredPosts.length;
    updateLightboxContent(filteredPosts[currentLightboxIndex]);
}

function updateLightboxContent(post) {
    lightboxMedia.innerHTML = '';

    if (post.media_type_name === 'video' && post.video_url) {
        const video = document.createElement('video');
        video.controls = true;
        video.autoplay = true;

        if (post.downloaded_files && post.downloaded_files.length > 0) {
            video.src = getLocalMediaPath(post.downloaded_files[0]);
        } else {
            video.src = post.video_url;
        }

        lightboxMedia.appendChild(video);
    } else if (post.media_type_name === 'album' && post.downloaded_files && post.downloaded_files.length > 1) {
        // Create grid container for all album images
        const gridContainer = document.createElement('div');
        gridContainer.style.display = 'grid';
        gridContainer.style.gridTemplateColumns = 'repeat(auto-fit, minmax(200px, 1fr))';
        gridContainer.style.gap = '10px';
        gridContainer.style.maxWidth = '90vw';
        gridContainer.style.maxHeight = '70vh';
        gridContainer.style.overflowY = 'auto';

        // Show all images/videos in the album
        post.downloaded_files.forEach((file, idx) => {
            const itemContainer = document.createElement('div');
            itemContainer.style.position = 'relative';
            itemContainer.style.cursor = 'pointer';
            itemContainer.style.borderRadius = '8px';
            itemContainer.style.overflow = 'hidden';

            // Check if it's a video or image based on file extension
            const isVideo = file.toLowerCase().endsWith('.mp4') || file.toLowerCase().endsWith('.mov');

            if (isVideo) {
                const video = document.createElement('video');
                video.src = getLocalMediaPath(file);
                video.style.width = '100%';
                video.style.height = '200px';
                video.style.objectFit = 'cover';
                video.controls = true;
                video.onerror = function() {
                    itemContainer.innerHTML = '<div style="background: #333; padding: 20px; color: white;">Video failed to load</div>';
                };
                itemContainer.appendChild(video);
            } else {
                const img = document.createElement('img');
                img.src = getLocalMediaPath(file);
                img.alt = `Album image ${idx + 1}`;
                img.style.width = '100%';
                img.style.height = '200px';
                img.style.objectFit = 'cover';
                img.style.display = 'block';
                img.onerror = function() {
                    if (post.thumbnail_url && idx === 0) {
                        img.src = post.thumbnail_url;
                    }
                };

                // Click to view full size
                img.addEventListener('click', function() {
                    const fullImg = document.createElement('img');
                    fullImg.src = img.src;
                    fullImg.style.maxWidth = '90vw';
                    fullImg.style.maxHeight = '90vh';
                    fullImg.style.objectFit = 'contain';

                    lightboxMedia.innerHTML = '';
                    lightboxMedia.appendChild(fullImg);

                    // Add back button
                    const backBtn = document.createElement('button');
                    backBtn.textContent = '← Back to grid';
                    backBtn.style.position = 'absolute';
                    backBtn.style.top = '20px';
                    backBtn.style.left = '20px';
                    backBtn.style.background = 'rgba(0,0,0,0.7)';
                    backBtn.style.color = 'white';
                    backBtn.style.border = 'none';
                    backBtn.style.padding = '10px 20px';
                    backBtn.style.borderRadius = '8px';
                    backBtn.style.cursor = 'pointer';
                    backBtn.style.fontSize = '14px';
                    backBtn.addEventListener('click', () => updateLightboxContent(post));
                    lightboxMedia.appendChild(backBtn);
                });

                itemContainer.appendChild(img);
            }

            gridContainer.appendChild(itemContainer);
        });

        lightboxMedia.appendChild(gridContainer);

        // Album info
        const albumInfo = document.createElement('div');
        albumInfo.style.color = 'white';
        albumInfo.style.marginTop = '15px';
        albumInfo.style.textAlign = 'center';
        albumInfo.textContent = `📷 Album with ${post.downloaded_files.length} items - Click any image to enlarge`;
        lightboxMedia.appendChild(albumInfo);
    } else {
        const img = document.createElement('img');

        if (post.downloaded_files && post.downloaded_files.length > 0) {
            img.src = getLocalMediaPath(post.downloaded_files[0]);
        } else if (post.thumbnail_url) {
            img.src = post.thumbnail_url;
        }

        img.alt = post.caption || 'Instagram post';
        img.onerror = function() {
            if (post.thumbnail_url && !img.src.includes('http')) {
                img.src = post.thumbnail_url;
            }
        };
        lightboxMedia.appendChild(img);
    }

    // Caption
    lightboxCaption.innerHTML = `
        <strong>@${post.user}</strong>
        ${post.caption ? `<br>${escapeHtml(post.caption)}` : ''}
    `;
}

// Keyboard Navigation
function handleKeyPress(event) {
    if (lightbox.style.display === 'flex') {
        switch(event.key) {
            case 'Escape':
                closeLightbox();
                break;
            case 'ArrowLeft':
                navigateLightbox(-1);
                break;
            case 'ArrowRight':
                navigateLightbox(1);
                break;
        }
    }
}

// Utility Functions
function showLoading() {
    loadingDiv.style.display = 'block';
    errorDiv.style.display = 'none';
    instructionsDiv.style.display = 'none';
}

function hideLoading() {
    loadingDiv.style.display = 'none';
}

function showError() {
    hideLoading();
    errorDiv.style.display = 'block';
    instructionsDiv.style.display = 'none';
}

function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML.replace(/\n/g, '<br>');
}

function formatDate(dateString) {
    if (!dateString) return null;

    try {
        // Parse the date string (format: "2025-10-23 17:49:37")
        const date = new Date(dateString.replace(' ', 'T'));

        // Get time (HH:MM)
        const hours = date.getHours().toString().padStart(2, '0');
        const minutes = date.getMinutes().toString().padStart(2, '0');
        const time = `${hours}:${minutes}`;

        // Get day with ordinal suffix
        const day = date.getDate();
        const suffix = ['th', 'st', 'nd', 'rd'][day % 10 > 3 ? 0 : (day % 100 - day % 10 !== 10) * day % 10];

        // Get month name
        const months = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December'];
        const month = months[date.getMonth()];

        // Get year
        const year = date.getFullYear();

        return `${time} | ${day}${suffix} ${month}, ${year}`;
    } catch (e) {
        return dateString; // Return original if parsing fails
    }
}

// Close lightbox when clicking outside content
lightbox.addEventListener('click', function(e) {
    if (e.target === lightbox) {
        closeLightbox();
    }
});
