#!/bin/bash

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

echo -e "python输出\n"

python3 ./st_01.py

echo -e "\npython文件执行完毕"

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
