#!/bin/bash
# OpenClaw 启动入口 - 转发到 start_services.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec bash "$SCRIPT_DIR/start_services.sh" "$@"
