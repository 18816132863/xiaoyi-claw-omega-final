#!/bin/bash

set -e

WEIXIN_LOGIN_LOG="/tmp/openclaw-weixin-login.log"

echo "========================================="
echo " OpenClaw Weixin 安装脚本"
echo "========================================="

# 步骤1：执行 npm pack 下载 tgz 包
echo ""
echo "[步骤 1/3] 正在下载 @tencent-weixin/openclaw-weixin@latest ..."
TGZ_FILE=$(npm pack @tencent-weixin/openclaw-weixin@latest 2>&1 | tail -n 1)

if [ ! -f "$TGZ_FILE" ]; then
  echo "❌ 错误：未找到下载的 tgz 文件：$TGZ_FILE"
  exit 1
fi

echo "✅ 下载成功：$TGZ_FILE"

# 步骤2：安装插件
echo ""
echo "[步骤 2/3] 正在安装插件：$TGZ_FILE ..."
NPM_CONFIG_REGISTRY=https://registry.npmmirror.com openclaw plugins install "$TGZ_FILE"
echo "✅ 插件安装成功"

# 步骤3：登录 channel（后台运行，避免阻塞超时）
echo ""
echo "[步骤 3/3] 正在启动微信扫码登录（后台运行）..."
echo "登录日志: $WEIXIN_LOGIN_LOG"

# 清理旧日志
> "$WEIXIN_LOGIN_LOG"

# 后台启动登录，输出重定向到日志文件
nohup openclaw channels login --channel openclaw-weixin > "$WEIXIN_LOGIN_LOG" 2>&1 &
LOGIN_PID=$!

echo "登录进程 PID: $LOGIN_PID"
echo ""

# 等待二维码生成（最多等30秒）
echo "⏳ 等待二维码生成..."
for i in $(seq 1 30); do
  if grep -q "liteapp.weixin.qq.com" "$WEIXIN_LOGIN_LOG" 2>/dev/null; then
    break
  fi
  sleep 1
done

# 提取二维码链接并输出
QRCODE_URL=$(grep -oP 'https://liteapp\.weixin\.qq\.com/q/[^\s]+' "$WEIXIN_LOGIN_LOG" | tail -1)

if [ -n "$QRCODE_URL" ]; then
  echo "✅ 二维码已生成"
  echo ""
  echo "QRCODE_URL=$QRCODE_URL"
  echo ""
  echo "========================================="
  echo " 安装完成！请用微信扫描以下链接中的二维码："
  echo " $QRCODE_URL"
  echo " ========================================="
  echo " 登录进程在后台运行中(PID: $LOGIN_PID)"
  echo " 可通过以下命令查看登录状态："
  echo "   cat $WEIXIN_LOGIN_LOG"
  echo "========================================="
else
  echo "⚠️ 未检测到二维码链接，请查看日志："
  echo "  cat $WEIXIN_LOGIN_LOG"
fi
