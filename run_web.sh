#!/bin/bash

# 🚀 在线商城数据库管理系统 - 快速启动脚本

echo "🏪 在线商城数据库管理系统"
echo "================================"
echo ""

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：找不到 Python 3"
    echo "请先安装 Python 3"
    exit 1
fi

echo "✅ Python 3 已找到"
echo ""

# 检查并安装依赖
echo "📦 检查依赖..."
pip3 install -q flask oracledb python-dotenv

echo "✅ 依赖已安装"
echo ""

# 启动 Web 应用
echo "🚀 启动 Web 应用..."
echo ""
echo "================================"
echo "访问地址: http://localhost:5000"
echo "================================"
echo ""

python3 web_app.py
