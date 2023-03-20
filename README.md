# 这是一个在chatGPt指导下完成的脚本和配置

# 在WSL系统启动时以管理员权限运行setproxy.py脚本

这份说明将指导您如何在WSL系统启动时以管理员权限运行setproxy.py脚本。

## 步骤

1. 打开WSL终端，进入setproxy.py脚本所在的目录。

2. 创建一个新的shell脚本文件，例如"run_setproxy.sh"，并在其中添加以下命令：

```bash
#!/bin/bash
sudo python3 /etc/init.d/setproxy.py
```

将setproxy.py和run_setproxy.sh文件放置在一个专门用于存放系统启动脚本的目录中，例如`/etc/init.d/` 或 `/usr/local/sbin/`。这些目录通常包含系统启动时需要运行的脚本文件。请注意，无论您选择将这些文件放置在哪个目录中，都应确保只有root用户和特定的系统服务可以访问和执行这些文件。可以通过更改文件的权限和所有权来限制访问。

例如，您可以使用以下命令将setproxy.py和run_setproxy.sh文件的所有权设置为root用户：

```bash
sudo chown root:root /path/to/run_setproxy.sh
```
然后，可以使用以下命令将这些文件的权限设置为仅限root用户可读写和执行：

```sudo chmod 700 /path/to/setproxy.py```

这将确保只有root用户可以访问和执行这些文件，从而提高系统的安全性。

3. 保存并关闭run_setproxy.sh文件。

4. 在终端中输入以下命令，将run_setproxy.sh文件设置为可执行文件：

chmod +x run_setproxy.sh


5. 然后，在终端中输入以下命令，打开系统的启动脚本文件：

sudo nano /etc/rc.local


6. 在文件的最后一行添加以下命令：

/etc/init.d/run_setproxy.sh &

如果没有这个文件则新建即可，在最开头要加上#!/bin/bash


其中，/etc/init.d/run_setproxy.sh应该替换为run_setproxy.sh文件的完整路径。

7. 保存并关闭rc.local文件。

8. 重新启动系统，setproxy.py脚本将在WSL系统启动时以管理员权限自动运行。

请注意，如果您的WSL系统是基于Ubuntu的，您可能需要将rc.local文件的权限设置为可写入，以便能够保存更改。您可以使用以下命令更改rc.local文件的权限：

sudo chmod +w /etc/rc.local

对于ubuntu 2204，可以在/lib/systemd/system/rc-local.service追加一段：

```
[Install]
WantedBy=multi-user.target
```

