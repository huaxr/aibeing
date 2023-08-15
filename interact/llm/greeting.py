# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com

import json
import os
from typing import Any
from datetime import datetime
from core.cache import redis_cli
from interact.handler.voice.microsoft import AudioTransform
from interact.llm.exception import AIBeingException
from interact.llm.base import AIBeingBaseTask
from interact.llm.template.greeting import greeting_template
from interact.llm.template.template import Template

class AIBeingGreetingTask(AIBeingBaseTask):
    def __init__(self, text2speech: AudioTransform, template: Template, expire: int=3600):
        super().__init__(text2speech)
        self.template = template
        self.expire = expire
    def get_current_time(self) -> str:
        current_datetime = datetime.now()
        year = current_datetime.strftime('%Y')
        month = current_datetime.month
        day = current_datetime.day

        current_date = datetime.now().date()
        weekday = current_date.weekday()
        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return  "今天日期: {year}年{month}月{day}日, {week}".format(year=year, month=month, day=day, week=weekdays[weekday])
    def generate(self) -> Any:
        key = self.rds_greeting_key.format(id=self.template.id, name=self.template.name)
        temp = self.template.get_character_prompt()
        if not temp:
            raise AIBeingException("No greeting prompt found for template:" + self.template.name)
        prompt = greeting_template.format(current_time=self.get_current_time()).replace("###", temp)
        res = self.proxy([self.system_message(prompt)], None, self.template.temperature, False)
        greeting_list = json.loads(res)
        values = []
        emotion = "excited"
        for i in greeting_list:
            filename = self.call_ms(i, self.template.voice, emotion)
            file_path = os.path.basename(filename)
            values.append({"text": i, "voice": file_path, "emotion": "excited"})
        print(values)
        redis_cli.set_value(key, json.dumps(values), self.expire)
        return 1
    async def async_generate(self) -> Any:
        raise NotImplementedError