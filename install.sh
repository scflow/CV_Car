#!/bin/bash

SCRIPT_PATH="$(pwd)/run.sh"

ALIAS="run2"

ALIAS_DEFINITION="
# Added by CV_Car install.sh script on $(date)
alias $ALIAS=\"$SCRIPT_PATH\"
# End of install.sh script section"

if [ ! -f "$SCRIPT_PATH" ]; then
  echo "$SCRIPT_PATH 不存在。"
  exit 1
fi

# 给 run.sh 增设可执行权限
chmod +x "$SCRIPT_PATH"

# 检查 requirements.txt 文件是否存在并安装依赖项
if [ -f "$REQUIREMENTS_PATH" ]; then
  echo "安装 requirements.txt 中的依赖项..."
  pip install -r "$REQUIREMENTS_PATH" || {
    echo "安装失败，尝试使用清华源重新安装..."
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r "$REQUIREMENTS_PATH"
  }
fi

if grep -q "# Added by install.sh script" ~/.bashrc; then
  echo "$ALIAS 已经存在于 .bashrc 中。"
else
  echo "$ALIAS_DEFINITION" >> ~/.bashrc
  echo "$ALIAS 已添加到 .bashrc 中。"
fi

source ~/.bashrc
echo -e "请执行命令:\n\tsource ~/.bashrc\n执行后生效"
