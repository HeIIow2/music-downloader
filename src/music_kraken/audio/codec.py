from typing import List, Tuple
import ffmpeg

from ..utils.shared import BITRATE, AUDIO_FORMAT, CODEX_LOGGER as LOGGER
from ..objects import Target


def remove_intervals(target: Target, interval_list: List[Tuple[float, float]]):
    if not target.exists:
        LOGGER.warning(f"Target doesn't exist: {target.file_path}")
        return
    
    # https://stackoverflow.com/questions/50594412/cut-multiple-parts-of-a-video-with-ffmpeg
    aselect_list: List[str] = []
    
    start = 0
    for end, next_start in interval_list:
        aselect_list.append(f"between(t,{start},{end})")
        
        start = next_start
        
    aselect_list.append(f"gte(t,{next_start})")
    
    select = f"aselect='{'+'.join(aselect_list)}',asetpts=N/SR/TB"


def correct_codec(target: Target, bitrate_kb: int = BITRATE, audio_format: str = AUDIO_FORMAT):
    if not target.exists:
        LOGGER.warning(f"Target doesn't exist: {target.file_path}")
        return

    bitrate_b = int(bitrate_kb / 1024)

    output_target = Target(
        path=target._path,
        file=str(target._file) + "." + audio_format
    )

    stream = ffmpeg.input(target.file_path)
    stream = stream.audio
    stream = ffmpeg.output(
        stream,
        str(output_target.file_path),
        audio_bitrate=bitrate_b,
        format=audio_format
    )
    out, err = ffmpeg.run(stream, quiet=True, overwrite_output=True)
    if err != "":
        LOGGER.debug(err)

    output_target.copy_content(target)
    output_target.file_path.unlink()
