# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com
import asyncio
import io
import json
import os
import random
import time
from typing import List, Any

import tiktoken
from langchain.chat_models import ChatOpenAI
from langchain import LLMChain, PromptTemplate
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate, BaseStringMessagePromptTemplate,
)

from core import conf
from core.conf import config
from core.log import logger
from core.cache import redis_cli
from core.db import ChatHistoryModel, create_chat
from interact.handler.voice.microsoft import AudioTransform
from interact.llm.exception import AIBeingException
from interact.llm.hook import AIBeingHook
from interact.llm.base import AIBeingBaseTask
from interact.llm.tools.search import GoogleAPIWrapper
from interact.schema.chat import response
from interact.schema.protocal import protocol
from interact.llm.template import chat, analyze
from interact.llm.template.template import  Vector, Voice, FewShot
from interact.llm.template.contichat import continue_template
from interact.llm.vector.client import VectorDB
class AIBeingChatTask(AIBeingBaseTask):
    def  __init__(self, uid: str, template_id: int, text2speech: AudioTransform, **kwargs):
        self.template = self.load_template(template_id)
        self.encoding = tiktoken.encoding_for_model(self.get_model_name(self.template.get_model()))
        if self.template.few_shot.switch:
            self.chat_list:List[BaseStringMessagePromptTemplate] = [Any for _ in range(len(self.template.few_shot.content) * 2 + 1)]
        else:
            self.chat_list: List[BaseStringMessagePromptTemplate] = [Any]
        self.text2speech = text2speech
        self.uid = uid
        self.template_id = template_id
        self.vector = VectorDB(config.llm_embedding_type)
        self.search = GoogleAPIWrapper()

        # for async only
        self._analyze_future = None
        self._analyze_future_result = None
        self._wait_analyze_times = 0
        super().__init__(**kwargs)

    # @chat_decorator
    def generate(self, inputs, **kwargs) -> Any:
        if inputs == protocol.get_greeting:
            return self.greeting()

        if inputs == protocol.get_continue_chat:
            return self.continue_chat()

        start = time.time()
        hook = kwargs["hook"]
        self.few_shot_example(self.template.fews)
        contexts = self.similarity(inputs, self.template.vec)
        ana_res = self.analyze(inputs)
        self.chat_list[0] = self.get_system_template(self.template.get_prompt(), "\n".join(contexts), ana_res, lang="cn")
        llm = self.get_llm(self.chat_list + [self.get_user_template(self.template.get_emotions())], hook, self.template.get_temperature(), self.template.get_model())
        input_size = self.input_tokens()
        res = llm.run(user_input=inputs)
        out_size = self.output_tokens(res)
        emotion, reply = self.handler_result(res)
        logger.info("emotion: {}, input: {}, reply: {}".format(emotion, inputs, reply))
        self.chat_list.append(HumanMessagePromptTemplate.from_template(inputs))
        self.chat_list.append(AIMessagePromptTemplate.from_template(reply))
        filename = self.call_ms(reply, self.template.voice, emotion)
        cost = self.get_total_cost(input_size, out_size, self.template.get_model())
        id = create_chat(ChatHistoryModel(template_id=self.template_id, uid=self.uid, input=inputs, output=reply, mp3=os.path.basename(filename), cost_time=time.time() - start, emotion=emotion, cost=cost))
        return response(protocol=protocol.chat_response, debug=reply, style=emotion, audio_url=os.path.basename(filename), template_id=self.template_id, chat_id=id).toStr()

    async def async_generate(self, inputs, **kwargs) -> Any:
        if inputs == protocol.get_greeting:
            return await self.async_greeting()

        if inputs == protocol.get_continue_chat:
            return await self.async_continue_chat()

        self.chat_list.append(HumanMessagePromptTemplate.from_template(inputs))

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
        hook = kwargs["hook"]
        self.few_shot_example(self.template.fews)
        contexts = await self.async_similarity(inputs, self.template.vec)
        self.chat_list[0] = self.get_system_template(self.template.get_prompt(), "\n".join(contexts), self._analyze_future_result, lang="cn")
        llm = self.get_llm(self.chat_list + [self.get_user_template(self.template.get_emotions())], hook, self.template.get_temperature(), self.template.get_model())
        input_size = self.input_tokens()
        res = await llm.arun(user_input=inputs)
        out_size = self.output_tokens(res)
        emotion, reply = self.handler_result(res)
        logger.info("emotion: {}, input: {}, reply: {}".format(emotion, inputs, reply))
        self.chat_list.append(AIMessagePromptTemplate.from_template(reply))
        filename = await self.async_call_ms(reply, self.template.voice, emotion)
        cost = self.get_total_cost(input_size, out_size, self.template.get_model())
        id = create_chat(ChatHistoryModel(template_id=self.template_id, uid=self.uid, input=inputs, output=reply, mp3=os.path.basename(filename), cost_time=time.time() - start, emotion=emotion, cost=cost))
        return response(protocol=protocol.chat_response, debug=reply, style=emotion, audio_url=os.path.basename(filename), template_id=self.template_id, chat_id=id).toStr()


    def handler_result(self, res: str) -> (str, str):
        dic = self.get_json(res)
        emotion = dic.get("emotion", "")
        reply = dic.get("reply", "")
        return emotion, reply

    def few_shot_example(self, few_shot_config: FewShot):
        if few_shot_config.switch:
            for data in few_shot_config.content:
                if len(data) != 2:
                    raise ValueError("few_shot content error")
                user, ai = data[0], data[1]
                example_human = SystemMessagePromptTemplate.from_template(
                    user, additional_kwargs={"name": "user_example"}
                )
                example_ai = SystemMessagePromptTemplate.from_template(
                    ai, additional_kwargs={"name": "assistant_example"}
                )
                self.chat_list[1] = example_human
                self.chat_list[2] = example_ai

    def get_llm(self, templates:Any, hook: AIBeingHook, temperature: float, model_type: str) -> LLMChain:
        llm = ChatOpenAI(temperature=temperature, streaming=conf.config.openai_streaming, callbacks=[hook],
                                       model_name=self.get_model_name(model_type=model_type))
        return LLMChain(llm=llm, prompt=ChatPromptTemplate.from_messages(templates))

    def call_ms(self, text, voice: Voice, emotion: str) -> str:
        if not voice.switch:
            return ""
        filename = self.text2speech.save_path + ".".join(["aib", str(time.time()), "mp3"])
        self.text2speech.text2audio(voice.style, emotion, text, filename)
        return filename

    async def async_call_ms(self, text: str, voice: Voice, emotion: str) -> str:
        if not voice.switch:
            return ""
        filename = self.text2speech.save_path + ".".join(["aib", str(time.time()), "mp3"])
        await self.text2speech.async_text2audio(voice.style, emotion, text, filename)
        return filename

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
        # logger.info("system template generated: {}".format(content))
        return SystemMessagePromptTemplate.from_template(content)

    def get_user_template(self, emotions):
        if emotions:
            prompt = getattr(chat, "chat_template_with_emotion", None).replace("###", emotions)
        else:
            prompt = getattr(chat, "chat_template_without_emotion", None)
        return HumanMessagePromptTemplate.from_template(prompt)

    def input_tokens(self) -> int:
        num_tokens = 0
        for i in self.chat_list:
            num_tokens += len(self.encoding.encode(i.prompt.template))
        return num_tokens

    def output_tokens(self, out: str) -> int:
         return len(self.encoding.encode(out))


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
            res = greeting_list[index]
            emotion = "excited"
            filename = self.call_ms(res, self.template.voice, emotion)
            self.chat_list.append(AIMessagePromptTemplate.from_template(res))
            return response(protocol=protocol.chat_response, debug=res, style=emotion,
                            audio_url=os.path.basename(filename), template_id=self.template_id).toStr()
        raise AIBeingException("greeting list is empty")

    async def async_greeting(self):
        key = self.rds_greeting_key.format(id=self.template.id, name=self.template.name)
        res = redis_cli.get_value(key)
        if res:
            greeting_list = json.loads(res)
            assert isinstance(greeting_list, list)
            index = random.randint(0, len(greeting_list) - 1)
            res = greeting_list[index]
            emotion = "excited"
            filename = await self.async_call_ms(res, self.template.voice, emotion)
            self.chat_list.append(AIMessagePromptTemplate.from_template(res))
            return response(protocol=protocol.chat_response, debug=res, style=emotion,
                            audio_url=os.path.basename(filename), template_id=self.template_id).toStr()
        raise AIBeingException("greeting list is empty")

    def analyze(self, inputs: str) -> str:
        try:
            history = self.get_chat_history()
            if len(history) == 0:
                return ""
            prompt = getattr(analyze, "analyze_conversation_with_input", None).replace("###", history).replace("$$$", inputs)
            # logger.info("analyze prompt: {}".format(prompt))
            prompt = PromptTemplate.from_template(prompt)
            lm = ChatOpenAI(temperature=self.template.temperature, model_name=self.get_model_name(model_type=self.template.model))
            llm = LLMChain(llm=lm, prompt=prompt)
            res = llm.predict()
            dic = json.loads(res)
            return getattr(analyze, "generate_analyze_prompt", None)(dic)
        except Exception as e:
            logger.error(e)
            return ""

    async def async_analyze(self) -> str:
        try:
            history = self.get_chat_history()
            if len(history) == 0:
                return ""
            prompt = getattr(analyze, "analyze_conversation", None).replace("###", history)
            prompt = PromptTemplate.from_template(prompt)
            llm = LLMChain(llm=ChatOpenAI(temperature=self.template.temperature, model_name=self.get_model_name(model_type=self.template.model)), prompt=prompt)
            res = await llm.apredict()
            dic = json.loads(res)
            assert isinstance(dic, dict)
            return getattr(analyze, "generate_analyze_prompt", None)(dic)
        except Exception as e:
            logger.error(e)
            return ""

    def get_chat_history(self, last_pair=6) -> str:
        messages = []
        for i in self.chat_list[-last_pair*2:]:
            if not isinstance(i, BaseStringMessagePromptTemplate):
                continue
            if len(i.additional_kwargs) > 0:
                continue

            if isinstance(i, AIMessagePromptTemplate):
                messages.append("AI:" + i.prompt.template)

            if isinstance(i, HumanMessagePromptTemplate):
                messages.append("User:" + i.prompt.template)
        return "\n".join(messages)

    def get_continue_llm(self) -> LLMChain:
        history = self.get_chat_history()
        prompt = continue_template.replace("$$$", history).replace("###", self.template.character_prompt)
        return LLMChain(llm=ChatOpenAI(temperature=self.template.temperature), prompt=PromptTemplate.from_template(prompt))

    def continue_chat(self):
        llm = self.get_continue_llm()
        res = llm.predict()
        filename = self.call_ms(res, self.template.voice, "chat")
        self.chat_list.append(AIMessagePromptTemplate.from_template(res))
        return response(protocol=protocol.get_continue_chat_rsp, debug=res, style="chat", audio_url=os.path.basename(filename), template_id=self.template_id).toStr()

    async def async_continue_chat(self):
        llm = self.get_continue_llm()
        res = await llm.apredict()
        filename = await self.async_call_ms(res, self.template.voice, "chat")
        self.chat_list.append(AIMessagePromptTemplate.from_template(res))
        return response(protocol=protocol.get_continue_chat_rsp, debug=res, style="chat", audio_url=os.path.basename(filename), template_id=self.template_id).toStr()