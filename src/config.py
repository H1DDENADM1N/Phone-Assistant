from dataclasses import dataclass
from pathlib import Path

logger_level = "INFO"


@dataclass(frozen=True)
class Paths:
    call_recording_dir: Path = Path.cwd() / "Call Recording"
    caps_writer_offline_dir: Path = Path(r"C:\Users\user0\Documents\CapsWriter-Offline")
    ffmpeg_path: Path = caps_writer_offline_dir / "ffmpeg.exe"
    start_client_gui_path: Path = caps_writer_offline_dir / "start_client_gui.exe"
