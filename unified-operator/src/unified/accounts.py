"""Account isolation: track exactly which identity (platform + account) is used
for every operation. Never mix Google/Discord/voice/OpenClaw identities."""
from __future__ import annotations

from .errors import Validation


class AccountRegistry:
    def __init__(self, settings):
        self.s = settings
        # platform -> default account id
        self._defaults = {
            "google": settings.google_account,
            "discord": settings.discord_account,
            "voice": settings.voice_agent_id or "business-number",
            "openclaw": "local",
            "meet": settings.google_account,
        }

    def resolve(self, platform: str, account: str | None = None) -> str:
        if platform not in self._defaults:
            raise Validation(f"unknown platform '{platform}'; expected one of "
                             f"{sorted(self._defaults)}")
        return account or self._defaults[platform]

    def accounts(self) -> dict:
        out = {}
        for p, a in self._defaults.items():
            out[p] = {"default_account": a}
        # Google account is config keyed; list from env identity only.
        return out

    def tag(self, platform: str, account: str | None) -> str:
        return f"{platform}::{self.resolve(platform, account)}"
