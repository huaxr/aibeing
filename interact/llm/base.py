# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com
import base64
import json
import os
import time
from io import BytesIO
from typing import Any, Union, List, Optional

import aiohttp
import requests
import tiktoken
from PIL import Image

from core.conf import config
from core.db import get_template_by_id, TemplateModel
from core.log import logger
from interact.handler.voice.microsoft import AudioTransform
from interact.llm.exception import AIBeingException
from interact.llm.hook import Hook
from interact.llm.template.template import Template, Vector, Voice, FewShot
from interact.llm.functions import available_functions

class AIBeingBaseTask(object):
    def __init__(self, text2speech: Optional[AudioTransform] = None):
        self.text2speech = text2speech
        self.rds_greeting_key = "{id}-{name}-greeting"
        self.encoding = tiktoken.encoding_for_model("gpt-4")

    def generate(self, *args, **kwargs) -> Any:
        raise NotImplementedError
    async def async_generate(self, *args, **kwargs) -> Any:
        raise NotImplementedError

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

    def _tokens(self, messages: List) -> int:
        num_tokens = 0
        for i in messages:
            content = i.get("content", None)
            if content:
                num_tokens += len(self.encoding.encode(content))
        return num_tokens

    def clip_tokens(self, chat_list):
        token_count = self._tokens(chat_list)
        if token_count > config.llm_max_token:
            if len(chat_list) > 3:  # 5 7 9
                chat_list = [chat_list[0]] + chat_list[-(len(chat_list) - 1):]
            else:
                chat_list = [chat_list[0]]
        return chat_list

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

    def prepare_proxy_header_data(self, messages: List[str], streaming: bool, temperature: float, functions: List = None, model_name:str="msai") -> ({}, {}, bool):
        headers = {"Content-Type": "application/json"}
        streaming = False if functions else streaming

        if model_name == "msai":
            headers["api-key"] = os.environ.get("PROXY_KEY")
            data = {"messages": messages, "stream": streaming, "temperature": temperature}
            llm_addr = "http://msai.tal.com/openai/deployments/gpt-4/chat/completions?api-version=2023-07-01-preview"
        elif model_name.startswith("gpt"):
            headers["Authorization"] = "Bearer " + os.environ.get("OPENAI_API_KEY")
            assert model_name in ["gpt-4", "gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4-32k"]
            data = {"messages": messages, "stream": streaming, "temperature": temperature, "model": model_name}
            llm_addr = "https://api.openai.com/v1/chat/completions"
        else:
            raise AIBeingException("unknown model_name {}".format(model_name))

        if functions:
            data["functions"] = functions
        return headers, data, streaming, llm_addr

    def agent(self, response_message:dict) -> dict:
        reason = response_message["choices"][0]["finish_reason"]
        call_res = response_message["choices"][0]["message"]
        logger.info("finish_reason:{} \n call_res:{}".format(reason, call_res))

        if reason == "function_call":
            # get exec result
            function_call_dict = call_res["function_call"]
            function_name = function_call_dict["name"]
            arguments = function_call_dict["arguments"]
            try:
                arguments_dic = json.loads(arguments)
                code = arguments_dic["code"]
            except Exception:
                logger.error(f"arguments is not dict: {arguments}")
                code = arguments

            callable = available_functions[function_name]
            exec_result = callable(code)
            logger.info("exec_result type:{}".format(exec_result.type))

            if exec_result.type == "image/png":
                image_bytes = base64.b64decode(exec_result.content)
                # 将字节数据转换为 Image 对象（使用 Pillow 库）
                image = Image.open(BytesIO(image_bytes))
                # 保存图片到文件
                file = "{}output_image.{}.png".format(config.image_path, time.time())
                image.save(file, "PNG")
                call_res["exec_result"] = file

            elif exec_result.type == "text":
                call_res["exec_result"] = exec_result.content

            elif exec_result.type == "error":
                call_res["exec_result"] = exec_result.content

            else:
                raise RuntimeError("unknown exec result type:" + exec_result.type)
            call_res["exec_type"] = exec_result.type
            # call_res.pop("role")
            # call_res.pop("function_call")
            return call_res
        elif reason == "stop":  # cot end
            return {"exec_type": "stop", "exec_result": call_res["content"]}

        else:
            raise RuntimeError("unknown function call reason:" + reason)

    async def async_agent(self, response_message:dict) -> dict:
        reason = response_message["choices"][0]["finish_reason"]
        call_res = response_message["choices"][0]["message"]
        logger.info("finish_reason:{} \n call_res:{}".format(reason, call_res))

        if reason == "function_call":
            # get exec result
            function_call_dict = call_res["function_call"]
            function_name = function_call_dict["name"]
            arguments = function_call_dict["arguments"]
            try:
                arguments_dic = json.loads(arguments)
                code = arguments_dic["code"]
            except Exception:
                logger.error(f"arguments is not dict: {arguments}")
                code = arguments

            callable = available_functions[function_name+"_async"]
            exec_result = await callable(code)
            logger.info("exec_result type:{}".format(exec_result.type))
            if exec_result.type == "image/png":
                image_bytes = base64.b64decode(exec_result.content)
                image = Image.open(BytesIO(image_bytes))
                file = "{}output_image.{}.png".format(config.image_path, time.time())
                image.save(file, "PNG")
                call_res["exec_result"] = file

            elif exec_result.type == "text":
                call_res["exec_result"] = exec_result.content

            elif exec_result.type == "error":
                call_res["exec_result"] = exec_result.content

            else:
                raise RuntimeError("unknown exec result type:" + exec_result.type)
            call_res["exec_type"] = exec_result.type
            return call_res
        elif reason == "stop":  # cot end
            return {"exec_type": "stop", "exec_result": call_res["content"]}

        else:
            raise RuntimeError("unknown function call reason:" + reason)

    def proxy(self, messages:List, hook:Union[Hook,None], temperature:float=0.7, streaming:bool=False, functions: Optional[List]=None, model_name:str = "msai") ->  Any:
        assert len(messages) > 0, "messages length must > 0"
        if functions:
            temperature = 0.03

        headers, data, streaming, llm_addr = self.prepare_proxy_header_data(messages, streaming, temperature, functions, model_name=model_name)
        if streaming:
            if hook.is_pure:
                hook.stream_pure_start()

            response = requests.post(llm_addr, headers=headers, json=data, stream=True)
            if response.status_code != 200:
                raise AIBeingException(f"proxy status code is: {response.status_code}, response is: {response.text}")

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
            response = requests.post(llm_addr, headers=headers, json=data, stream=False)
            if response.status_code != 200:
                raise AIBeingException(f"proxy status code is: {response.status_code}, response is: {response.text}")

            response_message = response.json()
            if functions:
                return self.agent(response_message)

            res = response_message["choices"][0]["message"]["content"]
            return res

    async def async_proxy(self, messages:List, hook:Union[Hook,None]=None, temperature:float=0.7, streaming:bool=False, functions: List=None, model_name:str = "msai") -> Any:
        assert len(messages) > 0, "messages length must > 0"
        if functions:
            temperature = 0.1

        headers, data, streaming, llm_addr = self.prepare_proxy_header_data(messages, streaming, temperature, functions, model_name=model_name)
        async with aiohttp.ClientSession() as session:
            if streaming:
                # 手动触发
                if hook.is_pure:
                    await hook.stream_pure_start()
                else:
                    await hook.stream_chat_token("{")

                async with session.post(llm_addr, headers=headers, json=data, timeout=None) as response:
                    if response.status != 200:
                        response_text = await response.text()
                        raise AIBeingException(f"proxy status code is: {response.status}, response is: {response_text}")

                    res, buffer = "", b""
                    async for chunk in response.content.iter_any():
                        if b'"error":' in chunk:
                            raise AIBeingException("streaming error from msai")

                        buffer += chunk
                        while b"\n\n" in buffer:
                            line, buffer = buffer.split(b"\n\n", 1)
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
                                raise AIBeingException(f"loads error, data: {json_data}")
                            delta = parsed_data['choices'][0]['delta']
                            content = delta.get("content", None)
                            if content:
                                res += content
                                if hook.is_pure:
                                    await hook.stream_pure_token(content)
                                else:
                                    await hook.stream_chat_token(content)

            else:
                async with session.post(llm_addr, headers=headers, json=data, timeout=None) as response:
                    if response.status != 200:
                        response_text = await response.text()
                        raise AIBeingException(f"proxy status code is: {response.status}, response is: {response_text}")

                    json_response = await response.json()
                    if functions:
                        res = await self.async_agent(json_response)
                        return res
                    return json_response["choices"][0]["message"]["content"]

    def system_message(self, content) -> dict:
        return {"role": "system", "content": content}
    def user_message(self, content) -> dict:
        return {"role": "user", "content": content}
    def ai_message(self, content, function_call = None) -> dict:
        """ {
              'role': 'assistant',
              'content': '好的，首先我们需要加载数据并查看其内容。让我们使用 pandas 库来完成这个任务。',
              'function_call': {'name': 'python', 'arguments': '{\n"code": "import pandas as pd\\n\\n# Load the data\\niris = pd.read_csv(\'iris.csv\')\\n\\n# Display the first few rows of the data\\niris.head()"\n}'}
            }
        """
        dic = {"role": "assistant", "content": content}
        if function_call:
            dic["function_call"] = function_call
        return dic

    def func_message(self, content, name) -> dict:
        """ {'role': 'function', 'content': 'function result', 'name': 'python'}"""
        return {"role": "function", "content": content, "name":name}

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