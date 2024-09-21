#!/bin/bash

# 设置默认Python文件名
default_py_file="st_gpio.py"

# 检查是否提供了参数
if [ $# -eq 0 ]; then
    echo "No file specified, running default Python file: $default_py_file"
    filename="$default_py_file"
else
    filename="$1"
fi

start_time=$(date +%s.%3N)

SCRIPT_DIR=$(dirname "$(realpath "$0")")

cd "$SCRIPT_DIR" || exit

# 防pigpio抽风
sudo systemctl stop network-rc.service
sudo killall pigpiod
sudo pigpiod
sudo systemctl stop network-rc.service

echo pigpio预处理完成, 准备执行python文件

sleep 1

if [ ! -f "$filename" ]; then
    echo "Error: Python file '$filename' not found."
    exit 1
fi

echo -e "python输出\n"

python3 "$filename"

if [ $? -ne 0 ]; then
    echo "Error: Failed to execute Python file '$filename'."
    exit 1
fi

echo "'$filename' executed successfully."

sudo killall pigpiod
sudo pigpiod
sudo systemctl restart network-rc.service

# 获取局域网IP地址
LAN_IP=$(hostname -I | awk '{print$1}')

# 检查是否成功获取IP地址
if [ -z "$LAN_IP" ]; then
  echo "无法获取局域网IP地址。"
  exit 1
fi

echo "network-rc已恢复访问: http://$LAN_IP:8001"

end_time=$(date +%s.%3N)
elapsed_time=$(bc <<< "scale=3;$end_time - $start_time")

echo "脚本执行完毕，用时: $elapsed_time 秒"
