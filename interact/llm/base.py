# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com
import json
import os
import time
from typing import Any, Union, List

import aiohttp
import langchain
import requests
from langchain.cache import InMemoryCache
from core.db import get_template_by_id, TemplateModel
from core.log import logger
from interact.handler.voice.microsoft import AudioTransform
from interact.llm.exception import AIBeingException
from interact.llm.hook import Hook
from interact.llm.template.template import Template, Vector, Voice, FewShot
from interact.llm.functions import available_functions

class AIBeingBaseTask(object):

    def __init__(self, text2speech: AudioTransform):
        self.text2speech = text2speech
        self.rds_greeting_key = "{id}-{name}-greeting"
        self.msai = "http://msai.tal.com/openai/deployments/gpt-4/chat/completions?api-version=2023-07-01-preview"
        # self.msai = "http://msai.tal.com/openai/deployments/gpt-4/chat/completions?api-version=2023-05-15"
        self.msai_key = os.environ.get("PROXY_KEY")

    def generate(self, *args, **kwargs) -> Any:
        raise NotImplementedError
    async def async_generate(self, *args, **kwargs) -> Any:
        raise NotImplementedError

    @classmethod
    def enable_cache(cls):
        langchain.llm_cache = InMemoryCache()

    def get_json(self, text) -> {}:
        start_index = text.find("{")
        end_index = text.find("}")
        if start_index != -1 and end_index != -1:
            json_str = text[start_index:end_index + 1]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                raise AIBeingException("JSON loads error:"+text)
        raise AIBeingException("No JSON found:"+text)

    def get_model_name(self, model_type:str) -> str:
        if model_type == "gpt-4":
            return "gpt-4"
        if model_type == "gpt-4-32k":
            return "gpt-4-32k"
        if model_type == "gpt-3.5":
            return "gpt-3.5-turbo"
        if model_type == "gpt-3.5-16k":
            return "gpt-3.5-turbo-16k"
        raise RuntimeError("No model found for type:"+model_type)

    def get_model_input_cost(self, model_type:str) -> float:
        if model_type == "gpt-4":
            return 0.03 / 1000
        if model_type == "gpt-4-32k":
            return 0.06 / 1000
        if model_type == "gpt-3.5":
            return 0.0015 / 1000
        if model_type == "gpt-3.5-16k":
            return 0.003 / 1000
        raise RuntimeError("No model found for type:"+model_type)

    def get_model_outout_cost(self, model_type:str) -> float:
        if model_type == "gpt-4":
            return 0.06 / 1000
        if model_type == "gpt-4-32k":
            return 0.12 / 1000
        if model_type == "gpt-3.5":
            return 0.002 / 1000
        if model_type == "gpt-3.5-16k":
            return 0.004 / 1000
        raise RuntimeError("No model found for type:"+model_type)

    def get_total_cost(self, intput_size: int, output_size: int,  model_type: str) -> str:
        inp = self.get_model_input_cost(model_type) * intput_size
        out = self.get_model_outout_cost(model_type) * output_size
        return str(round(inp + out, 5))

    def model2template(self, template_model: TemplateModel) -> Template:
        name = template_model.name
        avatar = template_model.avatar
        temperature = template_model.temperature
        model = template_model.model
        prompt = template_model.prompt
        character_prompt = template_model.character_prompt
        emotions = template_model.voice_emotion
        if len(emotions) == 0:
            emotions = "[]"

        few_shot_content = template_model.few_shot_content
        if len(few_shot_content) == 0:
            few_shot_content = "[]"
        voiceStruct = Voice(template_model.voice_switch, template_model.voice_style, json.loads(emotions))
        vectorStruct = Vector(template_model.vector_switch, template_model.vector_collection,
                              template_model.vector_top_k)
        few_shotStruct = FewShot(template_model.few_shot_switch, json.loads(few_shot_content))
        return Template(template_model.id, name, avatar, temperature, model, voiceStruct, vectorStruct, few_shotStruct,
                        prompt, character_prompt)
    def load_template(self, template_id:int) -> Union[Template, None]:
        # todo: load from cache
        template_model = get_template_by_id(template_id)
        if template_model is None:
            logger.error("No template found for id, may be pure chat:"+str(template_id))
            return None
        return self.model2template(template_model)

    def prepare_header_data(self, messages: List[str], streaming: bool, temperature: float, functions: List = None) -> ({}, {}, bool):
        headers = {
            "Content-Type": "application/json",
            "api-key": self.msai_key
        }

        streaming = False if functions else streaming
        data = {"messages": messages, "stream": streaming, "temperature": temperature}
        if functions:
            data["functions"] = functions

        return headers, data, streaming

    def proxy(self, messages:List, hook:Union[Hook,None], temperature:float=0.7, streaming:bool=False, functions: List=None) ->  Any:
        assert len(messages) > 0, "messages length must > 0"
        if functions:
            temperature = 0.03
        headers, data, streaming = self.prepare_header_data(messages, streaming, temperature, functions)
        if streaming:
            if hook.is_pure:
                hook.stream_pure_start()

            response = requests.post(self.msai, headers=headers, json=data, stream=True)
            assert response.status_code == 200, "proxy status code is: {}".format(response.status_code)
            res = ""
            for chunk in response.iter_lines(chunk_size=1024):
                if chunk:
                    data_str = chunk.decode('utf-8')
                    if data_str.__contains__("[DONE]"):
                        if hook.is_pure:
                            hook.stream_pure_end()
                        return res
                    json_start = data_str.find('{')
                    json_data = data_str[json_start:]
                    try:
                        parsed_data = json.loads(json_data)
                    except Exception:
                        logger.error(f"loads error, data: {json_data}")
                        raise AIBeingException("loads error from msai")
                    delta = parsed_data['choices'][0]['delta']
                    content = delta.get("content", None)

                    if content:
                        res += content
                        if hook.is_pure:
                            hook.stream_pure_token(content)
                        else:
                            hook.stream_chat_token(content)
        else:
            response = requests.post(self.msai, headers=headers, json=data, stream=False)
            assert response.status_code == 200, "proxy status code is: {}".format(response.status_code)
            response_message = response.json()
            if functions and response_message["choices"][0]["finish_reason"] == "function_call":
                call_res = response_message["choices"][0]["message"]
                function_call_dict = call_res["function_call"]
                function_name = function_call_dict["name"]
                code = json.loads(function_call_dict["arguments"])["code"]
                callable = available_functions[function_name]
                result = callable(code)
                call_res["result"] = result
                call_res["name"] = function_name
                return call_res

            res = response_message["choices"][0]["message"]["content"]
            return res

    async def async_proxy(self, messages:List, hook:Union[Hook,None], temperature:float=0.7, streaming:bool=False) -> str:
        assert len(messages) > 0, "messages length must > 0"
        headers, data, streaming = self.prepare_header_data(messages, streaming, temperature)
        async with aiohttp.ClientSession() as session:
            if streaming:
                # 手动触发
                if hook.is_pure:
                    await hook.stream_pure_start()
                else:
                    await hook.stream_chat_token("{")

                async with session.post(self.msai, headers=headers, json=data, timeout=None) as response:
                    assert response.status == 200, f"proxy status code is: {response.status}"
                    res, buffer = "", b""
                    async for chunk in response.content.iter_any():
                        logger.info(f"chunk: {chunk}")
                        buffer += chunk
                        while b"\n" in buffer:
                            line, buffer = buffer.split(b"\n", 1)
                            if len(line) == 0:
                                continue
                            data_str = line.decode('utf-8')
                            if data_str.__contains__("[DONE]"):
                                if hook.is_pure:
                                    await hook.stream_pure_end()
                                return res
                            json_start = data_str.find('{')
                            json_data = data_str[json_start:]
                            try:
                                parsed_data = json.loads(json_data)
                            except Exception:
                                logger.error(f"loads error, data: {json_data}")
                                raise AIBeingException("loads error from msai")
                            delta = parsed_data['choices'][0]['delta']
                            content = delta.get("content", None)
                            if content:
                                res += content
                                if hook.is_pure:
                                    await hook.stream_pure_token(content)
                                else:
                                    await hook.stream_chat_token(content)

            else:
                async with session.post(self.msai, headers=headers, json=data, timeout=None) as response:
                    assert response.status == 200, "proxy status code is: {}".format(response.status)
                    json_response = await response.json()
                    return json_response["choices"][0]["message"]["content"]

    def system_message(self, content) -> dict:
        return {"role": "system", "content": content}
    def user_message(self, content) -> dict:
        return {"role": "user", "content": content}
    def ai_message(self, content, function_call = None) -> dict:
        return {"role": "assistant", "content": content, "function_call": function_call}
    def func_message(self, content, call_name) -> dict:
        return {"role": "function", "content": content, "name":call_name}

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