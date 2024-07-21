import subprocess
import sys
import time
from pathlib import Path

from loguru import logger
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from .config import Paths, logger_level
from .write_md import write_md


class Watcher:
    def __init__(self):
        self.observer = Observer()
        self.CALL_RECORDING_PATH = Paths.call_recording_dir

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.CALL_RECORDING_PATH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            self.observer.stop()
            logger.info("Observer Stopped")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            self.observer.stop()
            logger.info("Observer Stopped due to error")

        self.observer.join()


class Handler(FileSystemEventHandler):
    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None
        FILE_PATH = Path(event.src_path)
        TXT_PATH = FILE_PATH.with_suffix(".txt")

        if (
            event.event_type == "modified"
            and is_audio(FILE_PATH)
            and not TXT_PATH.exists()
            and not is_using_by_others(FILE_PATH)
        ):
            logger.info(
                f"监测到音频文件修改，没有对应的txt文件，未被其他程序占用 - {FILE_PATH}"
            )
            is_valid, msg = check_audio_integrity(FILE_PATH)
        else:
            # logger.debug(f"非音频文件 或 文件被占用 或 已有对应的txt文件 - {FILE_PATH}")
            return None

        if is_valid:
            logger.info(f"音频文件完整 - {FILE_PATH}")
            gen_txt(FILE_PATH)
        else:
            logger.error(f"音频文件损坏 - {FILE_PATH}\n错误信息 - {msg}")


def is_audio(FILE_PATH):
    """
    判断文件是否为音频文件
    """
    if "_temp" in FILE_PATH.stem:
        return False  # 临时文件不处理

    suffix = Path(FILE_PATH).suffix
    return suffix in (".mp3", ".wav", ".aac", ".flac", ".m4a", ".ogg", ".opus")


def is_using_by_others(FILE_PATH):
    """
    尝试重命名文件来判断是否被占用。
    """
    try:
        logger.debug(f"尝试重命名文件来判断是否被占用 - {FILE_PATH}")
        # 创建一个临时文件名
        temp_file_path = FILE_PATH.with_name(f"{FILE_PATH.stem}_temp{FILE_PATH.suffix}")

        # 尝试重命名文件
        FILE_PATH.rename(temp_file_path)

        # 重命名成功，文件未被占用，将文件名改回原样
        temp_file_path.rename(FILE_PATH)
        logger.debug(f"文件未被占用 - {FILE_PATH}")
        return False  # 文件未被占用

    except OSError as e:
        # 如果重命名失败，则可能是因为文件被占用
        if "WinError 32" in str(e):
            logger.debug(f"文件被占用 - {FILE_PATH}")
            return True  # 文件被占用
        else:
            logger.error(f"is_using_by_others 执行过程中出现错误: {e}")
            return False  # 未知错误


def check_audio_integrity(FILE_PATH):
    """
    检查音频文件的完整性
    """
    # 使用ffmpeg命令尝试获取音频文件的详细信息
    FFMPEG_PATH = Paths.ffmpeg_path
    try:
        process = subprocess.Popen(
            f'{FFMPEG_PATH} -i "{FILE_PATH}"',
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True,
        )
        stdout, stderr = process.communicate()
        stdout = stdout.decode("utf-8")
        # 检查输出中是否包含错误信息
        if "Invalid data found when processing input" in stdout:
            return False, "音频文件损坏"
        elif "Duration" in stdout:
            return True, "音频文件完整"
        else:
            return False, "无法识别的音频文件问题"
    except Exception as e:
        return False, f"check_audio_integrity 执行过程中出现错误: {e}"


def gen_txt(FILE_PATH):
    """
    连接CapsWriter-Offline，识别音频并生成txt文件
    """
    try:
        logger.info(f"正在生成txt文件 - {FILE_PATH}")
        process = subprocess.Popen(
            f'"{Paths.start_client_gui_path}" "{FILE_PATH}"',
            creationflags=subprocess.CREATE_NO_WINDOW,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            text=True,
        )
        stdout, stderr = process.communicate()
        if stderr:
            logger.error(f"生成txt文件失败 - {FILE_PATH}\n错误信息 - {stderr}")
        else:
            start_time = time.perf_counter()
            durination = 0
            while not FILE_PATH.with_suffix(".txt").exists():
                if durination > 5:
                    logger.error(f"生成txt文件超时 - {FILE_PATH}")
                    break
                time.sleep(1)  # wait for subprocess to generate txt file
                durination = time.perf_counter() - start_time
            logger.info(f"已生成txt文件 - {FILE_PATH}")

            logger.info(f"正在写入markdown文件 - {FILE_PATH}")
            file_md = write_md(FILE_PATH)
            logger.info(f"已写入markdown文件 - {file_md}")
    except Exception as e:
        logger.critical(f"gen_txt 执行过程中出现错误: {e}")
    finally:
        process.kill()


def paths_check():
    """
    检查 config.py 中的路径设置是否正确
    """
    # 检查录音文件夹是否存在
    if not Paths.call_recording_dir.exists():
        logger.critical(
            f"录音文件夹不存在，请检查 config.py 中的 call_recording_dir 路径设置 - {Paths.call_recording_dir}"
        )
        sys.exit(1)
    # 检查ffmpeg.exe 和 caps_writer_offline start_client_gui.exe 是否存在
    if not Paths.ffmpeg_path.exists():
        logger.critical(
            f"ffmpeg 路径不存在，请检查 config.py 中的 caps_writer_offline_dir 路径设置 - {Paths.ffmpeg_path}"
        )
        sys.exit(1)
    if not Paths.start_client_gui_path.exists():
        logger.critical(
            f"caps_writer_offline start_client_gui.exe 路径不存在，请检查 config.py 中的 caps_writer_offline_dir 路径设置 - {Paths.start_client_gui_path}"
        )
        sys.exit(1)


def gen_txt_for_files_which_already_in_dir():
    """
    检查录音文件夹内现有录音文件是否有未生成txt文件的情况并生成txt文件
    """
    for file in Paths.call_recording_dir.iterdir():
        if (
            is_audio(file)
            and not is_using_by_others(file)
            and not file.with_suffix(".txt").exists()
        ):
            logger.info(f"发现现有录音文件未生成txt，正在生成 - {file}")
            gen_txt(file)
            logger.info(f"已生成txt文件 - {file}")


def main():
    logger.remove()
    logger.add(sink=sys.stdout, level=logger_level)

    logger.info("Phone-Assistant 程序启动")
    # 检查 config.py 中的路径设置是否正确
    paths_check()
    # 检查录音文件夹内现有录音文件是否有未生成txt文件的情况并生成txt文件
    gen_txt_for_files_which_already_in_dir()

    watcher = Watcher()
    watcher.run()
