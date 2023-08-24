# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com
import queue
import sys
import threading
import traceback
import uuid
import asyncio

import openai
import websockets
from typing import Union
from websockets.exceptions import WebSocketException

from core.log import logger
from core.conf import config
from interact.handler import handler
from interact.handler.voice.microsoft import AudioTransform
from interact.llm.base import AIBeingBaseTask
from interact.llm.chat import AIBeingChatTask
from interact.llm.hook import AIBeingHook, AIBeingHookAsync
from interact.schema.chat import response
from interact.schema.protocal import protocol

class WSServer(object):
    def __init__(self, port:int):
        self.port = port
        # linux only not darwin
        self.use_async = config.llm_async
        self.audiotrans = AudioTransform(save_path=config.audio_save_path)
        self.handler = handler.StreamHandler(audiotrans=self.audiotrans)

    async def asyncall_websocket_handler(self, websocket, path):
        session_id = str(uuid.uuid4())
        task: Union[AIBeingBaseTask, None] = None
        current_template_id = 0
        logger.info("session start %s" % session_id)
        while 1:
            try:
                message = await websocket.recv()
                if len(message) == 0:
                    await websocket.send(response(protocol=protocol.exception, debug="should not empty").toStr())
                    continue
                data, template_id, responseDirectly = await self.handler.async_on_message(message)
                data = data.toStr() if isinstance(data, response) else str(data)
                if responseDirectly:
                    await websocket.send(data)
                    continue
                if len(data) == 0:
                    await websocket.send(response(protocol=protocol.exception, debug="data input is empty").toStr())
                    continue

                # when pure chat, template_id is -1
                if task is None or template_id != current_template_id:
                    current_template_id = template_id
                    task = AIBeingChatTask(session_id, template_id, self.audiotrans)

                aiSay = await task.async_generate(data, hook=AIBeingHookAsync(websocket, template_id))
                await websocket.send(aiSay)

            except Exception as e:
                if isinstance(e, WebSocketException):
                    await websocket.close()
                    logger.info("session closed %s" %session_id)
                    break
                elif isinstance(e, openai.OpenAIError):
                    excepts = "openai exception! %s" % (str(e))
                elif isinstance(e, asyncio.CancelledError):
                    excepts = "async future task exception! %s" % (str(e))
                else:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    error_stack = traceback.format_tb(exc_traceback)
                    errors = []
                    for line in error_stack:
                        errors.append(line)
                    logger.error("\n".join(errors))
                    excepts = f"internal exception! {exc_type.__name__}: {exc_value}"
                logger.error(excepts)
                await websocket.send(response(protocol=protocol.exception, debug=excepts).toStr())

    def streaming_token(self, queue: queue.Queue, websocket):
        while True:
            item = queue.get()
            if item is None:
                break
            item = item.toStr() if isinstance(item, response) else str(item)
            asyncio.run(websocket.send(item))
    async def websocket_handler(self, websocket, path):
        session_id = str(uuid.uuid4())
        token_queue = queue.Queue()
        streaming_token_thread = threading.Thread(target=self.streaming_token, args=(token_queue, websocket))
        streaming_token_thread.start()
        task: Union[AIBeingBaseTask, None] = None
        current_template_id = 0
        logger.info("session start %s" % session_id)

        while 1:
            message = await websocket.recv()
            if len(message) == 0:
                await websocket.send(response(protocol=protocol.exception, debug="should not empty").toStr())
                continue
            data, template_id, responseDirectly = self.handler.on_message(message)
            data = data.toStr() if isinstance(data, response) else str(data)
            if responseDirectly:
                await websocket.send(data)
                continue
            if len(data) == 0:
                await websocket.send(response(protocol=protocol.exception, debug="data input is empty").toStr())
                continue
            if task is None or template_id != current_template_id:
                current_template_id = template_id
                task = AIBeingChatTask(session_id, template_id, self.audiotrans)
            # aiSay = task.generate(data, hook=AIBeingHook(token_queue, template_id))
            aiSay = task.codeinterpreter(data)
            await websocket.send(aiSay)

    def exception_handler(self, loop, context):
        exception = context.get("exception")
        logger.error(f"【*_*】exception_handler: {exception}")

    def init_handler(self):
        if self.use_async:
            loop = asyncio.get_event_loop()
            loop.set_exception_handler(self.exception_handler)
            return self.asyncall_websocket_handler
        else:
            return self.websocket_handler

    def server(self):
        return websockets.serve(
            self.init_handler(),
            '0.0.0.0',
            self.port,
            ping_interval=None,
        )


def startapp(port):
    srv = WSServer(int(port) if port is not None else config.ws_port)
    start_server = srv.server()
    logger.info("websocket listening on: %d" %srv.port)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
