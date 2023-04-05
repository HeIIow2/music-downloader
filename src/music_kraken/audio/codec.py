from pathlib import Path

import ffmpeg

from ..utils.shared import BITRATE, CODEX_LOGGER as LOGGER
from ..objects import Target

def correct_codec(target: Target, bitrate: int = BITRATE):
    if not target.exists:
        LOGGER.warning(f"Target doesn't exist: {target.file_path}")
    
    output_file = Path(str(target.file_path) + ".out")
    
    # https://www.audioranger.com/audio-formats.php
    # https://kkroening.github.io/ffmpeg-python/index.html?highlight=audio#ffmpeg.output
    
    ffmpeg_out = ffmpeg.output(
        ffmpeg.input(target.file_path),
        output_file,
        audio_bitrate=bitrate,
        format="mp3"
    ).run()
    """
    
in_file = ffmpeg.input('input.mp4')
overlay_file = ffmpeg.input('overlay.png')
(
    ffmpeg
    .concat(
        in_file.trim(start_frame=10, end_frame=20),
        in_file.trim(start_frame=30, end_frame=40),
    )
    .overlay(overlay_file.hflip())
    .drawbox(50, 50, 120, 120, color='red', thickness=5)
    .output('out.mp4')
    .run()
)
    """
