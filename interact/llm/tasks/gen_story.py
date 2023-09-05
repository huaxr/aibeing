# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com
from typing import Any, List

from core.log import logger
from interact.llm import check_running
from interact.llm.tasks.base import AIBeingBaseTask
from interact.llm.hook import AIBeingHookAsync, AIBeingHook
from interact.schema.chat import response
from interact.schema.protocal import protocol


class AIBeingStoryTask(AIBeingBaseTask):
    def  __init__(self, uid: str):
        self.uid = uid
        super().__init__()

    async def async_gen_story(self, prompt_chains: List[str], hook: AIBeingHookAsync, temperature:float=0.9, model_name:str="msai"):
        await hook.send_raw(response(protocol=protocol.gen_story_start, debug=""))
        self.chat_list = self.chat_list[1:]
        for i in prompt_chains:
            self.chat_list.append(self.user_message(i))
            res = await self.async_proxy(self.chat_list, temperature=temperature, streaming=False, model_name=model_name)
            self.chat_list.append(self.ai_message(res))
            self.chat_list = self.clip_tokens(self.chat_list)
            await hook.send_raw(response(protocol=protocol.gen_story_action, debug="prompt:{} \n生成结果\n:{}".format(i, res)))
        self.chat_list = []
        return response(protocol=protocol.gen_story_end, debug="").toStr()

    def gen_story(self, prompt_chains: List[str], hook: AIBeingHook, temperature:float=0.9, model_name:str="msai"):
        hook.send_raw(response(protocol=protocol.gen_story_start, debug=""))
        self.chat_list = self.chat_list[1:]
        for i in prompt_chains:
            self.chat_list.append(self.user_message(i))
            res = self.proxy(self.chat_list, None, temperature, False, model_name=model_name)
            self.chat_list.append(self.ai_message(res))
            self.chat_list = self.clip_tokens(self.chat_list)
            hook.send_raw(response(protocol=protocol.gen_story_action, debug=res))
        self.chat_list = []
        return response(protocol=protocol.gen_story_end, debug="").toStr()

    @check_running
    async def async_generate(self, input_js, **kwargs) -> Any:
        hook = kwargs["hook"]
        pt = input_js.get("pt")
        assert pt == protocol.gen_story, "pt must be gen_story"
        theme = input_js.get("theme")
        prompts = input_js.get("prompts")
        temperature = input_js.get("temperature")
        model_name = input_js.get("model_name")
        logger.info("temperature:{} model_name:{}".format(temperature, model_name))
        assert isinstance(prompts, list), "prompts must be list"
        return await self.async_gen_story(prompts, hook, temperature=float(temperature), model_name=model_name)

    @check_running
    def generate(self, input_js, **kwargs) -> Any:
        hook = kwargs["hook"]
        pt = input_js.get("pt")
        assert pt == protocol.gen_story, "pt must be gen_story"
        theme = input_js.get("theme")
        prompts = input_js.get("prompts")
        assert isinstance(prompts, list), "prompts must be list"
        temperature = input_js.get("temperature")
        assert temperature is not None, "temperature should not be None"
        model_name = input_js.get("model_name")
        assert model_name is not None, "model_name should not be None"
        logger.info("temperature:{} model_name:{}".format(temperature, model_name))
        return self.gen_story(prompts, hook, temperature=float(temperature), model_name=model_name)