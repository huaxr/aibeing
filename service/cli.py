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
            message = input("\n请输入消息：")
            if message == "greeting":
                message = json.dumps({"pt": "get_greeting", "template_id": 1})
            await websocket.send(message)

            while True:
                response = await websocket.recv()
                data = json.loads(response)
                if data["pt"] == "stream_end":
                    break

                if data["pt"] == "stream_action":
                    token = data["txt"]
                    sys.stdout.write(token)
                    sys.stdout.flush()
                    continue

                if data["pt"] == "exception":
                    print(data["txt"] + "\n")
                    break


asyncio.get_event_loop().run_until_complete(send_message())
