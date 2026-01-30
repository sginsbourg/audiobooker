import asyncio
from abc import ABC, abstractmethod
from typing import Optional

try:
    from edge_tts import Communicate
except Exception:
    Communicate = None


class TTSProvider(ABC):
    @abstractmethod
    def synthesize(self, text: str, out_path: str, voice: Optional[str] = None):
        pass


class EdgeTTSProvider(TTSProvider):
    def __init__(self, voice="en-GB-RyanNeural", rate="0%"):
        if Communicate is None:
            raise RuntimeError("edge-tts not installed")
        self.voice = voice
        self.rate = rate

    def synthesize(self, text: str, out_path: str, voice: Optional[str] = None):
        voice = voice or self.voice

        async def _s():
            com = Communicate(text, voice=voice)
            await com.save(out_path)

        asyncio.run(_s())
