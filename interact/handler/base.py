# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com
import json
from typing import Dict

from core.db import TemplateModel, create_template, get_template_list, get_template_by_id, update_template, update_chat_like, update_chat_unlike
from interact.handler.voice.microsoft import TTSMS
from interact.llm.tasks.greeting import AIBeingGreetingTask
from interact.llm.template.template import Template
from interact.schema.chat import response
from interact.schema.protocal import protocol
from interact.handler.voice.microsoft import support_voice_type, support_voice_emotion

class BaseHandler(object):
    def __init__(self):
        self.audiotrans = TTSMS()

    # bool means response directly to the client
    def on_message(self, message) -> (str, int, bool):
        print("debug message: ", message)
        return message, -1, False

    async def async_on_message(self, message) -> (str, int, bool):
        raise NotImplementedError

    def get_model_from_json(self, dic:{}) -> TemplateModel:
        name = dic.get("name")
        assert len(name) > 0, "name should not be empty"

        avatar = dic.get("avatar")
        assert len(avatar) > 0, "avatar should not be empty"

        temperature = dic.get("temperature")
        assert temperature >= 0.0 and temperature <= 1.0, "temperature should be in [0.0, 1.0]"

        model = dic.get("model")
        assert model in ["gpt-4", "gpt-4-32k", "gpt-3.5", "gpt-3.5-16k"], "model should be in [gpt-4, gpt-4-32k, gpt-3.5, gpt-3.5-16k]"

        voice = dic.get("voice")
        assert voice is not None, "voice should not be None"
        voice_switch = voice.get("voice_switch")
        voice_style = voice.get("voice_style")
        voice_emotion = json.dumps(voice.get("voice_emotion")) if voice.get("voice_emotion") else "[]"
        if voice_switch:
            assert voice_style in support_voice_type, "voice_style should be in {}".format(support_voice_type)
            for i in voice.get("voice_emotion"):
                assert i in support_voice_emotion, "voice_emotion should be in {}".format(support_voice_emotion)

        vector = dic.get("vector")
        assert vector is not None, "vector should not be None"
        vector_switch = vector.get("vector_switch")
        vector_collection = vector.get("vector_collection")
        vector_top_k = vector.get("vector_top_k")
        if vector_switch:
            assert len(vector_collection) > 0 and vector_top_k > 0, "vector_collection should not be empty and vector_top_k should be greater than 0"

        few_shot = dic.get("few_shot")
        assert few_shot is not None, "few_shot should not be None"
        few_shot_switch = few_shot.get("few_shot_switch")
        few_shot_content = json.dumps(few_shot.get("few_shot_content")) if few_shot.get("few_shot_content") else "[]"

        prompt = dic.get("prompt")
        assert len(prompt) > 0, "prompt should not be empty"

        character_prompt = dic.get("character_prompt")
        assert len(character_prompt) > 0, "character_prompt should not be empty"

        return TemplateModel( name=name, avatar=avatar, temperature=temperature,
                              model=model,
                              voice_switch=voice_switch, voice_style=voice_style,
                              voice_emotion=voice_emotion,
                              vector_switch=vector_switch,
                              vector_collection=vector_collection,
                              vector_top_k=vector_top_k,
                              few_shot_switch=few_shot_switch,
                              few_shot_content=few_shot_content,
                              prompt=prompt, character_prompt=character_prompt)

    def process(self, js:{}) -> (Dict, bool):
        pt = js["pt"]

        if pt in  [protocol.chat_thinking, protocol.gen_story]:
            return js, False

        if pt == protocol.chat_template:
            id = js.get("template_id", None)
            if id :
                if int(id) <= 0:
                    js["pt"] = protocol.chat_pure
            return js, False

        if pt == "login":
            js["content"] = response(protocol=protocol.login, debug="ok")
            return js, True

        if pt == "ping":
            js["content"] = response(protocol=protocol.pong, debug="ok")
            return js, True

        if pt == "like":
            chat_id = js["txt"]
            update_chat_like(int(chat_id))
            js["content"] = response(protocol=protocol.like, debug="ok")
            return js, True

        if pt == "unlike":
            chat_id = js["txt"]
            update_chat_unlike(int(chat_id))
            js["content"] = response(protocol=protocol.unlike, debug="ok")
            return js, True

        if pt == "create_template":
            data = js["txt"]
            dic = json.loads(data)
            model = self.get_model_from_json(dic)
            try:
                temp = create_template(model)
                res = temp.model_to_dict()
            except Exception as e:
                res = str(e)

            js["content"] = response(protocol=protocol.create_template_rsp, debug=res)
            return js, True

        if pt == "get_template_list":
            res = get_template_list()
            list = []
            for i in res:
                list.append(i.model_to_dict())

            js["content"] = response(protocol=protocol.get_template_list_rsp, debug=list)
            return js, True

        if pt == "get_template_by_id":
            id = js["txt"]
            res = get_template_by_id(id)
            js["content"] = response(protocol=protocol.get_template_by_id_rsp, debug=res.model_to_dict())
            return js, True

        if pt == "update_template":
            id = int(js["template_id"])
            assert id > 0, "template_id must be greater than 0"
            data = js["txt"]
            dic = json.loads(data)
            model = self.get_model_from_json(dic)
            try:
                res = update_template(id, model)
            except Exception as e:
                res = "update_template error:" + str(e)

            js["content"] = response(protocol=protocol.update_template_rsp, debug=res)
            return js, True

        if pt == "flush_cache":
            id = int(js["template_id"])
            i = get_template_by_id(id)
            t = Template.model2template(i)
            task = AIBeingGreetingTask(TTSMS(), t, 3600)
            task.generate()
            js["content"] = response(protocol=protocol.flush_cache_rsp, debug="")
            return js, True

        raise RuntimeError("unknown pt: {}".format(pt))