from dataclasses import dataclass
from pathlib import Path

logger_level = "DEBUG"


@dataclass(frozen=True)
class Paths:
    caps_writer_offline_dir: Path = Path(r"C:\Users\user0\Documents\CapsWriter-Offline")
    call_recording_dir: Path = Path(
        r"C:\Users\user0\Desktop\kRecorder-v0.2-x64-vs2019\Records"
    )

    ffmpeg_path: Path = caps_writer_offline_dir / "ffmpeg.exe"
    start_client_gui_path: Path = caps_writer_offline_dir / "start_client_gui.exe"
