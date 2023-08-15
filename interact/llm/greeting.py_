# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com
import json
from typing import Any, Union
from langchain.chat_models import ChatOpenAI
from datetime import datetime
from langchain import  LLMChain
from langchain.prompts import PromptTemplate
from core.cache import redis_cli
from interact.llm.exception import AIBeingException
from interact.llm.hook import AIBeingHook
from interact.llm.base import AIBeingBaseTask
from interact.llm.template.greeting import greeting_template
from interact.llm.template.template import Template

class AIBeingGreetingTask(AIBeingBaseTask):
    def __init__(self, template: Template, expire: int=3600, **kwargs):
        super().__init__(**kwargs)
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
        llm = self.get_llm(None, None, self.template.get_temperature(), self.template.get_model())
        res = llm.predict()
        print(res)
        greeting_list = json.loads(res)
        redis_cli.set_value(key, json.dumps(greeting_list), self.expire)
        return 1
    async def async_generate(self) -> Any:
        key = self.rds_greeting_key.format(id=self.template.id, name=self.template.name)
        llm = self.get_llm(None, None, self.template.get_temperature(), self.template.get_model())
        res = await llm.apredict()
        print(res)
        greeting_list = json.loads(res)
        redis_cli.set_value(key, json.dumps(greeting_list), self.expire)
        return 1
    def get_llm(self, templates: Any, hook: Union[AIBeingHook, None], temperature: float,model_type: str) -> LLMChain:
        temp = self.template.get_character_prompt()
        if not temp:
            raise AIBeingException("No greeting prompt found for template:"+self.template.name)

        prompt = PromptTemplate.from_template(greeting_template.format(current_time=self.get_current_time()).replace("###", temp))
        print(prompt)
        return LLMChain(llm=ChatOpenAI(temperature=temperature, model_name=self.get_model_name(model_type=self.template.model)), prompt=prompt)