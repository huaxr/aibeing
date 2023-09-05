# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com
from typing import Any

from core.db import create_chat, PureChatModel
from interact.llm import check_running
from interact.llm.tasks.base import AIBeingBaseTask
from interact.schema.chat import response
from interact.schema.protocal import protocol

class AIBeingPureTask(AIBeingBaseTask):
    def  __init__(self, uid: str):
        self.uid = uid
        super().__init__()

    @check_running
    async def async_generate(self, input_js, **kwargs) -> Any:
        hook = kwargs["hook"]
        inputs = input_js.get("content")
        if not inputs:
            return response(protocol=protocol.exception, debug="content should not be empty").toStr()

        temperature = input_js.get("temperature")
        model_name = input_js.get("model_name")
        self.chat_list.append(self.user_message(inputs))
        res = await self.async_proxy(self.chat_list, hook, temperature, streaming=True, model_name=model_name)
        self.chat_list.append(self.ai_message(res))
        create_chat(PureChatModel(uid=self.uid, input=inputs, output=res))
        return response(protocol=protocol.chat_response, debug=res).toStr()

    @check_running
    def generate(self, input_js, **kwargs) -> Any:
        hook = kwargs["hook"]
        inputs = input_js.get("content")
        if not inputs:
            return response(protocol=protocol.exception, debug="content should not be empty").toStr()

        self.chat_list.append(self.user_message(inputs))
        res = self.proxy(self.chat_list[-8:], hook, 0.9, streaming=True)
        self.chat_list.append(self.ai_message(res))
        create_chat(PureChatModel(uid=self.uid, input=inputs, output=res))
        return response(protocol=protocol.chat_response, debug=res).toStr()