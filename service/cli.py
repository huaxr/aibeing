# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com

import asyncio
import json
import sys

import websockets

async def heartbeat(websocket):
    while True:
        try:
            await websocket.ping()
            await asyncio.sleep(10)  # 每隔10秒发送一次心跳消息
        except websockets.ConnectionClosedError:
            break
async def send_message():
    # wss://inschool.life/websocket
    async with websockets.connect('ws://127.0.0.1:8823', ping_interval=None) as websocket:
        asyncio.create_task(heartbeat(websocket))

        while True:
            message = json.dumps(
                {"pt": "chat_thinking", "content": input("请输入消息："), "file": "/tmp/iris.csv"})
                # {"pt": "gen_story", "template_id": -1, "txt": {"theme": "大禹治水", "prompts":["人物开场", "场景描述", "煽情对话"], "temperature":0.5, "model_name": "gpt-4"}})

            await websocket.send(message)

            while True:
                response = await websocket.recv()
                data = json.loads(response)
                print(data)
                break


asyncio.get_event_loop().run_until_complete(send_message())
