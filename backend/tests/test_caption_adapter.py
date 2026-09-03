from app.services.caption_adapter import adapt_caption, youtube_title


def test_adapt_caption_passes_through_when_under_limit():
    assert adapt_caption("Sepatu lari terbaru!", "instagram") == "Sepatu lari terbaru!"


def test_adapt_caption_truncates_instagram_and_tiktok_at_2200():
    long_caption = "x" * 2300
    for platform in ("instagram", "tiktok"):
        result = adapt_caption(long_caption, platform)
        assert len(result) == 2200
        assert result.endswith("…")


def test_adapt_caption_truncates_youtube_description_at_5000():
    result = adapt_caption("x" * 5100, "youtube")
    assert len(result) == 5000


def test_youtube_title_truncates_at_100():
    result = youtube_title("x" * 150)
    assert len(result) == 100
    assert result.endswith("…")


def test_youtube_title_passes_through_short_titles():
    assert youtube_title("Sepatu lari") == "Sepatu lari"
