import time
from pathlib import Path

from loguru import logger

from .config import Paths

header_md = r"""```txt
正则表达式 Tip

匹配到音频文件链接：\[(.+)\]\((.{10,})\)[\s]*
替换为 HTML 控件：<audio controls><source src="$2" type="audio/mpeg">$1</audio>\n\n

匹配 HTML 控件：<audio controls><source src="(.+)" type="audio/mpeg">(.+)</audio>\n\n
替换为文件链接：[$2]($1) 
```


"""


def create_md(file_md):
    try:
        with file_md.open("w", encoding="utf-8") as f:
            f.write(header_md)
    except Exception as e:
        logger.error(f"创建 markdown 文件 {file_md} 失败：{e}")


def write_md(file_audio: Path):
    file_txt = file_audio.with_suffix(".txt")
    try:
        with file_txt.open("r", encoding="utf-8") as f:
            text = f.read().strip("\n")
    except Exception as e:
        text = f"读取 {file_txt} 失败：{e}"
        logger.error(text)

    time_start = file_audio.stat().st_ctime  # 音频文件的创建时间
    time_year = time.strftime("%Y", time.localtime(time_start))
    time_month = time.strftime("%m", time.localtime(time_start))
    time_day = time.strftime("%d", time.localtime(time_start))
    time_hms = time.strftime("%H:%M:%S", time.localtime(time_start))

    folder_path = Paths.caps_writer_offline_dir / time_year / time_month
    if not folder_path.exists():
        folder_path.mkdir(parents=True, exist_ok=True)
    file_md = folder_path / f"{time_day}-Phone-Assistant.md"
    if not file_md.exists():
        create_md(file_md)

    # 写入 md
    with file_md.open("a", encoding="utf-8") as f:
        path_ = file_audio.resolve().as_posix().replace(" ", "%20")
        f.write(f"[{time_hms}]({path_}) {text}\n\n")

    return file_md
