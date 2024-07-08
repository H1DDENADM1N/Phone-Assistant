# Phone-Assistant

监测通话录音文件夹，有新的录音文件时，调用 [CapsWriter-Offline](https://github.com/H1DDENADM1N/CapsWriter-Offline)，将音频文件转换为同名 txt 文件。

Inspired by [请求监听转录功能 #31](https://github.com/H1DDENADM1N/CapsWriter-Offline/issues/31).

> 能否增加功能，实现这样的目的：打开客户端后，客户端立即开始监听设定好的麦克风，并在每段声音出现后转录成文字，将文字内容记入当天的文档中。
> 
> 设想：这个客户端可以与按下Caps的版本共存（不检测按键）；麦克风中没有声音3秒（可否自定义）就视为一段；
> 
> 使用背景：办公室有一台bbk录音电话（hcd-198），连接pc并安装话机软件后，会在windows中添加usb phone 的扬声器和usb phone的麦克风，有电话时会自动录音，电话软件也有留言录音功能。因不能一直守着电话，每次回来需要逐一听取是否有留言，所以想通过这个功能记录留言内容，在打开文档后就可以看到文字内容，节省逐一听取录音的时间。

#### TODO

- [ ] 调用AI分析txt并推送QQ/微信.

## 用法

1. `pip install -r requirements.txt`

2. 修改 `src/config.py` 文件，设置 `call_recording_dir` 和 `caps_writer_offline_dir` 。

3. 修改 CapsWriter-Offline `core_client.py` `main_file()` 函数，注释掉 `# input("\n按回车退出\n")`，否则subprocess无法退出，会在后台一直运行着多个`cmd.exe`和`python.exe`。

4. 先启动 [CapsWriter-Offline](https://github.com/H1DDENADM1N/CapsWriter-Offline) 服务端 `start_server_gui.exe`。

5. 再运行 `python phone_assistant.py`。