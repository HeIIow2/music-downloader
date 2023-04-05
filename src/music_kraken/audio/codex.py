import ffmpeg

from ..utils.shared import BITRATE
from ..objects import Target

def correct_codex(target: Target, bitrate: int = BITRATE):
    if not target.exists:
        pass
