#!/bin/bash
# 检查是否传入参数
if [ $# -ne 1 ]; then
    echo "Usage: $0 <text>"
    exit 1
fi
# 设置要发送的 JSON 数据
json_data='{"text":"'"$1"'"}'
echo "请求生成文件..."
# 发送 POST 请求获取文件名
response=$(curl -X POST -H "Content-Type: application/json" -d "$json_data" http://10.202.3.15:80/bark/generate)
echo "返回结果: $response"
file_name=$(echo $response | grep -o '"file":"[^"]*' | awk -F ':"' '{print $2}')
echo "获取文件名: $file_name"
# 下载文件到桌面
wget "http://10.202.3.15:80/file/$file_name" -P ~/Desktop
echo "文件下载完成 ~/Desktop/$file_name"
