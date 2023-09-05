# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com
from typing import Any

from core.conf import config
from core.log import logger
from interact.llm import check_running
from interact.llm.tasks.base import AIBeingBaseTask
from interact.llm.functions import functions
from interact.llm.hook import AIBeingHookAsync, AIBeingHook
from interact.llm.template import codecot
from interact.schema.chat import response
from interact.schema.protocal import protocol

class AIBeingCotTask(AIBeingBaseTask):
    def  __init__(self):
        super().__init__()

    async def async_codeinterpreter(self, user_input: str, file: str, hook: AIBeingHookAsync):
        sys = self.system_message(codecot.codeinterpreter_system.format(file_path=config.working_path))
        user = self.user_message(codecot.codeinterpreter_user.format(user_input=user_input, upload_file=file))
        self.chat_list[0] = sys
        self.chat_list.append(user)
        res = await self.async_proxy(self.chat_list, None, 0.03, streaming=False, functions=functions)
        while 1:
            typ = res.pop("exec_type")
            result = res.pop("exec_result")
            if typ == "stop":
                ai = self.ai_message(result)
                self.chat_list.append(ai)
                logger.info("stop 发送给客户端, 结束cot")
                return response(protocol=protocol.thinking_stop, debug=result).toStr()
            content = res.pop("content")
            logger.info("生成内容:{}".format(content))
            txt = "{}\n{}".format(content, result) if content else result
            if typ == "text":
                logger.info("text 发送给客户端")
                await hook.send_raw(response(protocol=protocol.thinking_now, debug=txt))
            if typ == "error":
                logger.info("error 发送给客户端, 结束cot")
                function_call = res.pop("function_call")
                name = function_call["name"]
                self.chat_list.append(self.func_message(result, name))
                return response(protocol=protocol.thinking_error, debug=txt).toStr()
            if typ == "image/png":
                logger.info("image 发送给客户端, {}".format(result))
                await hook.send_raw(response(protocol=protocol.thinking_image, file_name=result))
            function_call = res.pop("function_call")
            name = function_call["name"]
            ai = self.ai_message(content, function_call)
            func = self.func_message(result, name)
            self.chat_list.append(ai)
            self.chat_list.append(func)
            res = await self.async_proxy(self.chat_list, None, 0.03, streaming=False, functions=functions)

    def codeinterpreter(self, user_input: str, file: str, hook: AIBeingHook):
        sys = self.system_message(codecot.codeinterpreter_system.format(file_path=config.working_path) + codecot.codeinterpreter_urls)
        user = self.user_message(codecot.codeinterpreter_user.format(user_input=user_input, upload_file=file))
        self.chat_list[0] = sys
        self.chat_list.append(user)
        res = self.proxy(self.chat_list, None, 0.03, streaming=False, functions=functions)
        while 1:
            result = res.pop("exec_result")
            typ = res.pop("exec_type")
            if typ == "stop":
                ai = self.ai_message(result)
                self.chat_list.append(ai)
                return response(protocol=protocol.thinking_stop, debug=result).toStr()
            content = res.pop("content")
            txt = "{}\n{}".format(content, result) if content else result
            if typ == "text":
                hook.send_raw(response(protocol=protocol.thinking_now, debug=txt))
            if typ == "error":
                function_call = res.pop("function_call")
                name = function_call["name"]
                self.chat_list.append(self.func_message(result, name))
                return response(protocol=protocol.thinking_error, debug=txt).toStr()
            if typ == "image/png":
                hook.send_raw(response(protocol=protocol.thinking_image, file_name=result))

            function_call = res.pop("function_call")
            name = function_call["name"]
            ai = self.ai_message(content, function_call)
            func = self.func_message(result, name)
            self.chat_list.append(ai)
            self.chat_list.append(func)
            res = self.proxy(self.chat_list, None, 0.03, streaming=False, functions=functions)


    @check_running
    async def async_generate(self, input_js, **kwargs) -> Any:
        hook = kwargs["hook"]
        inputs = input_js.get("content")
        if not inputs:
            return response(protocol=protocol.exception, debug="content should not be empty").toStr()
        file = input_js.get("file")
        logger.info("chat thinking: {}".format(input_js))
        return await self.async_codeinterpreter(inputs, file, hook)
    @check_running
    def generate(self, input_js, **kwargs) -> Any:
        hook = kwargs["hook"]
        inputs = input_js.get("content")
        if not inputs:
            return response(protocol=protocol.exception, debug="content should not be empty").toStr()
        file = input_js.get("file", None)
        return self.codeinterpreter(inputs, file, hook)
