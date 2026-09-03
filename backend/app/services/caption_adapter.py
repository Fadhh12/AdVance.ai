"""Per-platform caption limits (SRS §2.2: IG ~2200, TikTok ~2200, YouTube title ~100 /
description ~5000). Pure functions, no ffmpeg/network — auto-truncates rather than just
rejecting an over-limit caption.
"""
CAPTION_LIMITS = {"instagram": 2200, "tiktok": 2200, "youtube": 5000}
YOUTUBE_TITLE_LIMIT = 100


def adapt_caption(caption: str, platform: str) -> str:
    limit = CAPTION_LIMITS[platform]
    return caption if len(caption) <= limit else caption[: limit - 1].rstrip() + "…"


def youtube_title(title: str) -> str:
    if len(title) <= YOUTUBE_TITLE_LIMIT:
        return title
    return title[: YOUTUBE_TITLE_LIMIT - 1].rstrip() + "…"
