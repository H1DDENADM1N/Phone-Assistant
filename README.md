# Phone-Assistant

监测通话录音文件夹，有新的录音文件时，调用 [CapsWriter-Offline](https://github.com/H1DDENADM1N/CapsWriter-Offline)，将音频文件转换为同名 txt 文件。

#### TODO

- [ ] 调用AI分析txt并推送QQ/微信.

## 用法

1. `pip install -r requirements.txt`

2. 修改 `src/config.py` 文件，设置 `call_recording_dir` 和 `caps_writer_offline_dir` 。

3. 先启动 [CapsWriter-Offline](https://github.com/H1DDENADM1N/CapsWriter-Offline) 服务端 `start_server_gui.exe`。

4. 再运行 `python phone_assistant.py`。