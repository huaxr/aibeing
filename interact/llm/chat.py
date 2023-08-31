# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com

import asyncio
import io
import json
import os
import random
import time
from typing import List, Any, Dict

from . import check_running
from core.conf import config
from core.log import logger
from core.cache import redis_cli
from core.db import ChatHistoryModel, create_chat, PureChatModel
from interact.handler.voice.microsoft import AudioTransform
from interact.llm.exception import AIBeingException
from interact.llm.base import AIBeingBaseTask
from interact.llm.hook import AIBeingHookAsync, AIBeingHook
from interact.schema.chat import response
from interact.schema.protocal import protocol
from interact.llm.template import chat, analyze, codecot
from interact.llm.template.template import  Vector
from interact.llm.vector.client import VectorDB
from interact.llm.functions import functions

class AIBeingChatTask(AIBeingBaseTask):
    def  __init__(self, uid: str, template_id: int, text2speech: AudioTransform):
        if template_id > 0:
            self.template = self.load_template(template_id)
            self.template_id = template_id

        self.chat_list: List[Dict] = [self.system_message("You can start to chat now!")]
        self.uid = uid
        self.vector = VectorDB(config.llm_embedding_type)
        # self.search = GoogleAPIWrapper()
        # for async only
        self._analyze_future = None
        self._analyze_future_result = None
        self._wait_analyze_times = 0
        super().__init__(text2speech)

    def gen_story(self, prompt_chains: List[str], hook: AIBeingHook, temperature:float=0.9, model_name:str="msai"):
        hook.send_text(protocol.gen_story_start, "")
        for i in prompt_chains:
            self.chat_list.append(self.user_message(i))
            self.chat_list = self.chat_list[1:]
            res = self.proxy(self.chat_list, None, temperature, False, model_name=model_name)
            self.chat_list.append(self.ai_message(res))
            self.chat_list = self.clip_tokens(self.chat_list)
            hook.send_text(protocol.gen_story_action, res)
        self.chat_list = []
        return response(protocol=protocol.gen_story_end, debug="").toStr()

    async def async_gen_story(self, prompt_chains: List[str], hook: AIBeingHookAsync, temperature:float=0.9, model_name:str="msai"):
        await hook.send_text(protocol.gen_story_start, "")
        for i in prompt_chains:
            self.chat_list.append(self.user_message(i))
            self.chat_list = self.chat_list[1:]
            res = await self.async_proxy(self.chat_list, temperature=temperature, streaming=False, model_name=model_name)
            self.chat_list.append(self.ai_message(res))
            self.chat_list = self.clip_tokens(self.chat_list)
            await hook.send_text(protocol.gen_story_action, "prompt:{} \n生成结果\n:{}".format(i, res))
        self.chat_list = []
        return response(protocol=protocol.gen_story_end, debug="").toStr()

    def codeinterpreter(self, user_input: str, file: str, hook: AIBeingHook):
        sys = self.system_message(codecot.codeinterpreter_system.format(file_path=config.working_path))
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

    @check_running
    def generate(self, input_js, **kwargs) -> Any:
        hook = kwargs["hook"]
        pt = input_js.get("pt")
        if pt == protocol.gen_story:
            theme = input_js.get("theme")
            prompts = input_js.get("prompts")
            assert isinstance(prompts, list), "prompts must be list"
            temperature = input_js.get("temperature")
            assert temperature is not None, "temperature should not be None"
            model_name = input_js.get("model_name")
            assert model_name is not None, "model_name should not be None"
            logger.info("temperature:{} model_name:{}".format(temperature, model_name))
            assert isinstance(prompts, list), "prompts must be list"
            return self.gen_story(prompts, hook, temperature=float(temperature), model_name=model_name)

        inputs = input_js.get("content")

        if not inputs:
            return response(protocol=protocol.exception, debug="content should not be empty").toStr()

        if pt == protocol.chat_thinking:
            file = input_js.get("file", None)
            assert file is not None, "file should not be None "
            return self.codeinterpreter(inputs, file, hook)

        if pt == protocol.chat_pure:
            self.chat_list.append(self.user_message(inputs))
            res = self.proxy(self.chat_list[-8:], hook, 0.9, streaming=True)
            self.chat_list.append(self.ai_message(res))
            create_chat(PureChatModel(uid=self.uid, input=inputs, output=res))
            return response(protocol=protocol.chat_response, debug=res).toStr()

        if pt == protocol.get_greeting:
            return self.greeting()

        start = time.time()
        contexts = self.similarity(inputs, self.template.vec)
        ana_res = self.analyze(inputs)
        self.chat_list[0] = self.get_system_template(self.template.get_prompt(), "\n".join(contexts), ana_res, lang="cn")
        chat_list = self.chat_list + [self.get_user_template(self.template.get_emotions(), inputs)]
        res = self.proxy(chat_list, hook, self.template.temperature, streaming=True)
        emotion, reply = self.handler_result(res)
        logger.info("emotion: {}, input: {}, reply: {}".format(emotion, inputs, reply))
        self.chat_list.append(self.user_message(inputs))
        self.chat_list.append(self.ai_message(reply))
        filename = self.call_ms(reply, self.template.voice, emotion)
        id = create_chat(ChatHistoryModel(template_id=self.template_id, uid=self.uid, input=inputs, output=reply, mp3=os.path.basename(filename), cost_time=time.time() - start, emotion=emotion, cost=0))
        return response(protocol=protocol.chat_response, debug=reply, style=emotion, audio_url=os.path.basename(filename), template_id=self.template_id, chat_id=id).toStr()

    @check_running
    async def async_generate(self, input_js, **kwargs) -> Any:
        hook = kwargs["hook"]
        pt = input_js.get("pt")

        if pt == protocol.gen_story:
            theme = input_js.get("theme")
            prompts = input_js.get("prompts")
            temperature = input_js.get("temperature")
            model_name = input_js.get("model_name")
            logger.info("temperature:{} model_name:{}".format(temperature, model_name))
            assert isinstance(prompts, list), "prompts must be list"
            return await self.async_gen_story(prompts, hook, temperature=float(temperature), model_name=model_name)

        inputs = input_js.get("content")
        if not inputs:
            return response(protocol=protocol.exception, debug="content should not be empty").toStr()

        if pt == protocol.chat_thinking:
            file = input_js.get("file")
            logger.info("chat thinking: {}".format(input_js))
            return await self.async_codeinterpreter(inputs, file, hook)

        # pure chat
        if pt == protocol.chat_pure:
            temperature = input_js.get("temperature")
            model_name = input_js.get("model_name")
            self.chat_list.append(self.user_message(inputs))
            res = await self.async_proxy(self.chat_list, hook, temperature, streaming=True, model_name=model_name)
            self.chat_list.append(self.ai_message(res))
            create_chat(PureChatModel(uid=self.uid, input=inputs, output=res))
            return response(protocol=protocol.chat_response, debug=res).toStr()

        if pt == protocol.get_greeting:
            return self.greeting()

        self.chat_list.append(self.user_message(inputs))

        if self._analyze_future is None:
            logger.info("_analyze_future is None, now create")
            self._analyze_future = asyncio.create_task(self.async_analyze())
        else:
            if self._analyze_future.done():
                logger.info("_analyze_future is done, now set _analyze_future_result and recreate task")
                self._analyze_future_result = self._analyze_future.result()
                self._analyze_future = asyncio.create_task(self.async_analyze())
                self._wait_analyze_times = 0
            else:
                self._wait_analyze_times += 1
                if self._wait_analyze_times > 2:
                    logger.info("_analyze_future not done exceed 2 times, now wait until done")
                    await self._analyze_future
                    assert self._analyze_future.done(), "analyze future not done yet after wait"
                    self._analyze_future_result = self._analyze_future.result()
                    self._wait_analyze_times = 0
                else:
                    logger.info("_analyze_future is not done, now continue, times:{}".format(self._wait_analyze_times))

        start = time.time()
        contexts = await self.async_similarity(inputs, self.template.vec)
        self.chat_list[0] = self.get_system_template(self.template.get_prompt(), "\n".join(contexts), self._analyze_future_result, lang="cn")
        chat_list = self.chat_list + [self.get_user_template(self.template.get_emotions(), inputs)]
        res = await self.async_proxy(chat_list, hook, self.template.temperature, streaming=True)
        emotion, reply = self.handler_result(res)
        logger.info("emotion: {}, input: {}, reply: {}}".format(emotion, inputs, reply))
        self.chat_list.append(self.ai_message(reply))
        filename = await self.async_call_ms(reply, self.template.voice, emotion)
        id = create_chat(ChatHistoryModel(template_id=self.template_id, uid=self.uid, input=inputs, output=reply, mp3=os.path.basename(filename), cost_time=time.time() - start, emotion=emotion, cost=0))
        return response(protocol=protocol.chat_response, debug=reply, style=emotion, audio_url=os.path.basename(filename), template_id=self.template_id, chat_id=id).toStr()

    def handler_result(self, res: str) -> (str, str):
        assert len(res) > 0, "result is empty"
        res = res.replace("\n", "")
        dic = self.get_json(res)
        emotion = dic.get("emotion", "")
        reply = dic.get("reply", "")
        return emotion, reply

    def handler_analyze_result(self, res: str) -> dict:
        assert len(res) > 0, "analyze result is empty"
        res = res.replace("\n", "")
        return self.get_json(res)
    def get_system_template(self, prompt, vec_context, _future, lang="en"):
        buffer = io.StringIO()
        v, a, i = "corpus_template", "analyze_template", "introduction_template"
        if lang == "cn":
            v += "_cn"
            a += "_cn"
            i += "_cn"
        corpus_template = getattr(chat, v, None)
        analyze_template = getattr(chat, a, None)
        intro_template = getattr(chat, i, None)
        buffer.write(intro_template.format(introduction_input=prompt))
        if vec_context:
            buffer.write(corpus_template.format(system_input=vec_context))
        if _future:
            buffer.write(analyze_template.format(analyze_input=_future))
        content = buffer.getvalue()
        buffer.close()
        logger.info("system template generated: {}".format(content))
        return self.system_message(content)

    def get_user_template(self, emotions, inputs):
        if emotions:
            prompt = getattr(chat, "chat_template_with_emotion", None).replace("###", emotions).format(user_input=inputs)
        else:
            prompt = getattr(chat, "chat_template_without_emotion", None).format(user_input=inputs)
        return  self.user_message(prompt)

    def similarity(self, inputs: str, config: Vector) -> List[str]:
        if config.switch:
            assert len(config.collection) > 0 and config.top_k > 0, "collection and top_k should be set"
            return self.vector.similarity(config.collection, inputs, config.top_k)
        return []

    async def async_similarity(self, inputs: str, config: Vector) -> List[str]:
        if config.switch:
            assert len(config.collection) > 0 and config.top_k > 0, "collection and top_k should be set"
            res =  await self.vector.async_similarity(config.collection, inputs, config.top_k)
            return res
        return []

    def greeting(self):
        key = self.rds_greeting_key.format(id=self.template.id, name=self.template.name)
        res = redis_cli.get_value(key)
        if res:
            greeting_list = json.loads(res)
            assert isinstance(greeting_list, list)
            index = random.randint(0, len(greeting_list) - 1)
            dic = greeting_list[index]
            emotion = dic.get("emotion", "excited")
            filename = dic.get("voice", "")
            text = dic.get("text", "")
            self.chat_list.append(self.ai_message(str(text)))
            return response(protocol=protocol.chat_response, debug=text, style=emotion,
                            audio_url=os.path.basename(filename), template_id=self.template_id).toStr()
        raise AIBeingException("greeting list is empty")

    def analyze(self, inputs: str) -> str:
        history = self.get_chat_history()
        if len(history) == 0:
            return ""
        prompt = getattr(analyze, "analyze_conversation_with_input", None).replace("###", history).replace("$$$", inputs)
        res = self.proxy([self.system_message(prompt)], None, self.template.temperature, False)
        dic = self.handler_analyze_result(res)
        return getattr(analyze, "generate_analyze_prompt", None)(dic)


    async def async_analyze(self) -> str:
        history = self.get_chat_history()
        if len(history) == 0:
            return ""
        prompt = getattr(analyze, "analyze_conversation", None).replace("###", history).replace("$$$", self.template.prompt)
        logger.info("analyze prompt: {}".format(prompt))
        res = await self.async_proxy([self.system_message(prompt)], None, self.template.temperature, False)
        dic = self.handler_analyze_result(res)
        assert isinstance(dic, dict)
        return getattr(analyze, "generate_analyze_prompt", None)(dic)

    def get_chat_history(self) -> str:
        messages = []
        for i in self.chat_list:
            role, content = i["role"], i["content"]
            if role == "user":
                messages.append("User:" + content)

            if role == "assistant":
                messages.append("AI:" + content)

        return "\n".join(messages)
