# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com
import asyncio
from interact.schema.chat import response
from interact.schema.protocal import protocol

class Hook(object):
    def __init__(self, is_pure: bool):
        self.is_pure = is_pure
    async def stream_chat_token(self, token: str) -> None: pass

    async def stream_pure_token(self, token: str) -> None: pass

    async def stream_pure_start(self) -> None: pass

    async def stream_pure_end(self) -> None: pass

class LCHook():
    pass

class AIBeingHookAsync(Hook):
    def __init__(self, sock, template_id: int):
        """Initialize callback handler."""
        self.sock = sock
        self.template_id = template_id
        self.content_format = '"reply":'
        self.current_sentence = ""

        self.stream_start_done = False
        self.stream_end_done = False
        super().__init__(is_pure=self.template_id <= 0)

    async def stream_chat_token(self, token: str) -> None:
        self.current_sentence += token

        if token.__contains__("{") and not self.stream_start_done:
            await self.sock.send(response(protocol=protocol.stream_start, template_id=self.template_id).toStr())
            self.stream_start_done = True

        if len(token) > 0 and self.current_sentence.__contains__(self.content_format) and not token.__contains__('"') and not token.__contains__("}"):
            await asyncio.sleep(0.05)
            await self.sock.send(response(protocol=protocol.stream_action, debug=token, template_id=self.template_id).toStr())

        if token.__contains__("}") and not self.stream_end_done:
            self.current_sentence = ""
            await self.sock.send(response(protocol=protocol.stream_end, template_id=self.template_id).toStr())
            self.stream_end_done = True
    async def stream_pure_token(self, token: str) -> None:
        await asyncio.sleep(0.05)
        await self.sock.send(response(protocol=protocol.stream_action, debug=token, template_id=self.template_id).toStr())
    async def stream_pure_start(self) -> None:
        await self.sock.send(response(protocol=protocol.stream_start, template_id=self.template_id).toStr())
    async def stream_pure_end(self) -> None:
        await self.sock.send(response(protocol=protocol.stream_end, template_id=self.template_id).toStr())

class AIBeingHook(Hook):
    """Callback Handler that prints to std out."""
    def __init__(self, queue, template_id):
        """Initialize callback handler."""
        self.q = queue
        self.template_id = template_id
        self.current_sentence = ""
        self.content_format = '"reply":'

        self.stream_start_done = False
        self.stream_end_done = False
        super().__init__(is_pure=self.template_id <= 0)

    def stream_chat_token(self, token: str) -> None:
        # uuid = str(kwargs["run_id"])
        self.current_sentence += token

        if token.__contains__("{"):
            self.q.put(response(protocol=protocol.stream_start, template_id=self.template_id).toStr())

        if len(token) > 0 and self.current_sentence.__contains__(self.content_format) and not token.__contains__('"') and not token.__contains__("}"):
            self.q.put(response(protocol=protocol.stream_action, debug=token, template_id=self.template_id).toStr())

        if token.__contains__("}"):
            self.current_sentence = ""
            self.q.put(response(protocol=protocol.stream_end, template_id=self.template_id).toStr())
    def stream_pure_token(self, token: str) -> None:
        self.q.put(response(protocol=protocol.stream_action, debug=token, template_id=self.template_id).toStr())

    def stream_pure_start(self) -> None:
        self.q.put(response(protocol=protocol.stream_start, template_id=self.template_id).toStr())
    def stream_pure_end(self) -> None:
        self.q.put(response(protocol=protocol.stream_end, template_id=self.template_id).toStr())