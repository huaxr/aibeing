# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com

import requests

# 代理服务器的地址和端口
proxy_host = "39169.applegamee.com"
proxy_port = 39169

# 代理服务器的用户名和密码
proxy_username = "HOST&PEER"
proxy_password = "eplcgame.com"

# 构造代理的 URL
proxy_url = f"http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}"

# 目标网址
target_url = "https://www.google.com"

# 设置代理并发送请求
response = requests.get(target_url, proxies={"http": proxy_url, "https": proxy_url})

# 打印响应内容
print(response.text)
