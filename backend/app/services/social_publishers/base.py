"""Abstract interface every social platform publisher wrapper will implement.

NOT implemented yet — Phase 6 (SDD Task Breakdown), blocked on Meta/TikTok/YouTube
developer app approval (see CLAUDE.md: "jangan berasumsi API pihak ketiga sudah bisa
dipakai"). This file only settles the contract shape ahead of time so `posts` model /
Publish Manual Assist (Phase 5) can be written against a stable interface, and Phase 6
later just adds `meta.py` / `tiktok.py` / `youtube.py` implementations here — no
changes needed elsewhere.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class PublishResult:
    success: bool
    platform_post_id: str | None = None
    error_message: str | None = None


class SocialPublisher(ABC):
    @abstractmethod
    def publish(self, video_url: str, caption: str) -> PublishResult:
        """Not called by any code path yet — Phase 5 uses manual download/share instead
        (FR-13). Wired up in Phase 6 once OAuth + developer app approval exist.
        """
        raise NotImplementedError
