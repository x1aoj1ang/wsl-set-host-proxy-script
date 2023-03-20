#!/usr/bin/env python3

import os
import socket
import struct
import fcntl
import subprocess
import re

# 网络地址和端口
NET_ADDRESS = "192.168.0.1"
PROXY_PORT = "1080"

# 获取第一个非本地网卡的IP地址和掩码
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_fd = sock.fileno()
SIOCGIFADDR = 0x8915
SIOCGIFNETMASK = 0x891b

# 获取所有网卡的信息
ifaces = []
try:
    ifaces = os.listdir('/sys/class/net/')
except OSError:
    # 如果无法访问/sys/class/net/，则使用ip命令获取网卡列表
    output = subprocess.check_output("ip link show | awk '{print $2}' | sed 's/://' | grep -vE '^lo$'", shell=True).decode().strip()
    ifaces = output.split("\n")

for iface in ifaces:
    if iface.startswith('lo'):
        continue
    try:
        # 获取IP地址
        ip_bytes = fcntl.ioctl(sock_fd, SIOCGIFADDR, struct.pack(b'256s', iface.encode()))[20:24]
        host_ip = socket.inet_ntoa(ip_bytes)

        # 获取掩码
        netmask_bytes = fcntl.ioctl(sock_fd, SIOCGIFNETMASK, struct.pack(b'256s', iface.encode()))[20:24]
        netmask = socket.inet_ntoa(netmask_bytes)

        # 计算网络地址
        ip_list = [int(x) for x in host_ip.split(".")]
        mask_list = [int(x) for x in netmask.split(".")]
        net_list = [ip_list[i] & mask_list[i] for i in range(4)]
        net_list[-1] += 1  # 加1得到广播地址
        net_address = ".".join([str(x) for x in net_list])

        print("Host IP: {}".format(host_ip))
        print("Mask: {}".format(netmask))
        print("Network Address: {}".format(net_address))

        # 设置Git代理
        try:
            subprocess.check_call(["git", "config", "--global", "http.proxy", "socks5://{0}:{1}".format(net_address, PROXY_PORT)])
            subprocess.check_call(["git", "config", "--global", "https.proxy", "socks5://{0}:{1}".format(net_address, PROXY_PORT)])
            print("Git proxy set to: socks5://{0}:{1}".format(net_address, PROXY_PORT))
        except subprocess.CalledProcessError:
            print("Error: failed to set Git proxy")

        # 设置Proxychains代理
        try:
            with open(os.devnull, "w") as devnull:
                subprocess.check_call(["proxychains", "-q", "echo", "Proxychains is working"], stdout=devnull)
            with open(os.path.expanduser("/etc/proxychains4.conf"), "r") as f:
                conf = f.read()
            conf = re.sub(r'socks\d+\s+\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\s+\d+\n', f'socks5 {net_address} {PROXY_PORT}\n', conf)
            with open(os.path.expanduser("/etc/proxychains4.conf"), "w") as f:
                f.write(conf)
            print("Proxychains proxy set to: socks5://{0}:{1}".format(net_address, PROXY_PORT))
        except (subprocess.CalledProcessError, IOError):
            print("Error: failed to set Proxychains proxy") 

        # 找到第一个非本地网卡的IP地址和掩码后退出循环
        break
    except IOError:
        # 如果获取IP地址和掩码失败，则继续尝试其他网卡
        continue
else:
    # 如果没有找到非本地网卡，则输出错误信息
    print("Error: no non-local network interface found")
