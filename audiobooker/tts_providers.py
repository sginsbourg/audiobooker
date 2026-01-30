import asyncio
"""TTS provider interface and Edge TTS implementation."""
from abc import ABC, abstractmethod
from typing import Optional, Any, cast

try:
    from edge_tts import Communicate as _Communicate
except ImportError:
    _Communicate = None

# For type-checking: allow calling Communicate via cast when it exists
CommunicateCallable: Any = _Communicate


class TTSProvider(ABC):
    """Abstract TTS provider interface."""

    @abstractmethod
    def synthesize(self, text: str, out_path: str, voice: Optional[str] = None):
        """Synthesize `text` to a file at `out_path` using optional voice id."""
        raise NotImplementedError


class EdgeTTSProvider(TTSProvider):
    """Edge TTS implementation using the `edge-tts` package."""

    def __init__(self, voice: str = "en-GB-RyanNeural", rate: str = "0%") -> None:
        if _Communicate is None:
            raise RuntimeError("edge-tts not installed")
        self.voice = voice
        self.rate = rate

    def synthesize(self, text: str, out_path: str, voice: Optional[str] = None) -> None:
        """Synthesize `text` into `out_path` using the configured voice."""
        voice = voice or self.voice

        async def _s() -> None:
            com = cast(Any, CommunicateCallable)(text, voice=voice)
            await com.save(out_path)

        asyncio.run(_s())
