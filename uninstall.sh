#!/bin/bash

ALIAS="run2"

# 定义要删除的别名部分
ALIAS_DEFINITION="# Added by CV_Car install.sh script on"

# 检查 ~/.bashrc 中是否存在要删除的别名定义
if grep -q "$ALIAS_DEFINITION" ~/.bashrc; then
  # 使用 sed 删除包含别名定义的行
  sed -i "/$ALIAS_DEFINITION/,/# End of install.sh script section/d" ~/.bashrc
  echo "$ALIAS 已从 .bashrc 中移除。"
else
  echo "$ALIAS 不存在于 .bashrc 中。"
fi

# 重新加载 .bashrc 以应用更改
source ~/.bashrc

echo "重启终端后生效"