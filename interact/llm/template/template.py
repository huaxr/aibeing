# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com
import json
from typing import List

from core.db import TemplateModel


class Voice:
    def __init__(self, switch: bool, style: str, emotions: List[str]):
        self.switch = switch
        self.style = style
        self.emotions = emotions

class Vector:
    def __init__(self, switch: bool, collection: str, top_k: int):
        self.switch = switch
        self.collection = collection
        self.top_k = top_k

class FewShot:
    def __init__(self, switch: bool, content: List[List[str]]):
        self.switch = switch
        self.content = content

class Template:
    def __init__(self, id: int, name: str, avatar: str, temperature: float, model:str, voice: Voice, vector: Vector, few_shot: FewShot, prompt: str, character_prompt:str):
        self.id = id
        self.name = name
        self.avatar = avatar
        self.temperature = temperature
        self.model = model
        self.voice = voice
        self.vector = vector
        self.few_shot = few_shot
        self.prompt = prompt
        self.character_prompt = character_prompt

    def get_temperature(self) -> float:
        return self.temperature


    def get_prompt(self) -> str:
        return self.prompt

    def get_character_prompt(self) -> str:
        return self.character_prompt

    def get_voice_style(self) -> str:
        return self.voice.style

    def get_emotions(self) -> str:
        return ",".join(self.voice.emotions)

    @property
    def vec(self) -> Vector:
        return self.vector

    @property
    def fews(self) -> FewShot:
        return self.few_shot

    def get_model(self) -> str:
        return self.model

    @classmethod
    def model2template(cls, template_model: TemplateModel):
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
        return cls(template_model.id, name, avatar, temperature, model, voiceStruct, vectorStruct, few_shotStruct,
                        prompt, character_prompt)