import ffmpeg

from ..utils.shared import BITRATE, AUDIO_FORMAT, CODEX_LOGGER as LOGGER
from ..objects import Target


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
