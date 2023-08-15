# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com
import json
from typing import List

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from core import conf
from interact.llm.exception import AIBeingException

engine = create_engine(conf.config.mysql_dsn)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class ChatHistoryModel(Base):
    __tablename__ = 'chat_history'
    id = Column(Integer, primary_key=True)
    template_id = Column(Integer)
    uid = Column(String(100))
    input = Column(Text)
    output = Column(Text)
    mp3 =  Column(Text)
    emotion = Column(String(100))
    cost_time = Column(Integer)
    cost = Column(String(100))
    like = Column(Boolean)
    create_time = Column(DateTime, default=datetime.now)

class TemplateModel(Base):
    __tablename__ = 'template'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    avatar = Column(String(100))
    temperature = Column(Float)
    model = Column(String(100))
    voice_switch = Column(Integer)
    voice_style = Column(String(100))
    voice_emotion = Column(String(100))
    vector_switch = Column(Integer)
    vector_collection = Column(String(100))
    vector_top_k = Column(Integer)
    few_shot_switch = Column(Integer)
    few_shot_content = Column(Text)
    prompt = Column(Text)
    character_prompt = Column(Text)
    create_time = Column(DateTime, default=datetime.now)

    def model_to_dict(self) -> dict:
        return {
            "id": self.get_id(),
            "name": self.get_name(),
            "avatar": self.get_avatar(),
            "temperature": self.get_temperature(),
            "model": self.get_model(),
            "voice": {"voice_switch": self.get_voice_switch(),
                      "voice_style": self.get_voice_style(),
                      "voice_emotion": self.get_voice_emotion()},
            "vector": {"vector_switch": self.get_vector_switch(), "vector_collection": self.get_vector_collection(),
                       "vector_top_k": self.get_vector_top_k()},
            "few_shot": {"few_shot_switch": self.get_few_shot_switch(),
                         "few_shot_content": self.get_few_shot_content()},
            "prompt": self.get_prompt(),
            "character_prompt": self.get_character_prompt(),
        }
    def get_id(self) -> int:
        return int(self.id.__str__())

    def get_name(self) -> str:
        return self.name.__str__()

    def get_avatar(self) -> str:
        return self.avatar.__str__()

    def get_temperature(self) -> float:
        return float(self.temperature.__str__())

    def get_model(self) -> str:
        return self.model.__str__()

    def get_voice_switch(self) -> int:
        return int(self.voice_switch.__str__())

    def get_voice_style(self) -> str:
        return self.voice_style.__str__()

    def get_voice_emotion(self) -> List[str]:
        if self.voice_emotion:
            return json.loads(self.voice_emotion.__str__())
        else:
            return []

    def get_vector_switch(self) -> int:
        return int(self.vector_switch.__str__())

    def get_vector_collection(self) -> str:
        return self.vector_collection.__str__()

    def get_vector_top_k(self) -> int:
        return int(self.vector_top_k.__str__())

    def get_few_shot_switch(self) -> int:
        return int(self.few_shot_switch.__str__())

    def get_few_shot_content(self) -> List[List[str]]:
        if self.few_shot_content:
            return json.loads(self.few_shot_content.__str__())
        else:
            return [[]]

    def get_prompt(self) -> str:
        return self.prompt.__str__()

    def get_character_prompt(self) -> str:
        return self.character_prompt.__str__()

def update_chat_like(id: int):
    session = Session()
    existing_chat = session.query(ChatHistoryModel).filter_by(id=id).first()
    if existing_chat:
        existing_chat.like = 1
        session.commit()
        session.close()
    else:
        raise AIBeingException('chat not found, id:%d' % id)

def update_chat_unlike(id: int):
    session = Session()
    existing_chat = session.query(ChatHistoryModel).filter_by(id=id).first()
    if existing_chat:
        existing_chat.like = 0
        session.commit()
        session.close()
    else:
        raise AIBeingException('chat not found, id:%d' % id)

def create_chat(chat: ChatHistoryModel) -> int:
    session = Session()
    session.add(chat)
    session.commit()
    id = chat.id
    session.close()
    return int(id.__str__())

def create_template(temp: TemplateModel) -> TemplateModel:
    res = temp
    session = Session()
    session.add(temp)
    session.commit()
    res.id = temp.id
    session.close()
    return res

def update_template(id: int, temp: TemplateModel) -> {}:
    session = Session()
    existing_template = session.query(TemplateModel).filter_by(id=id).first()

    if existing_template:
        existing_template.name = temp.name
        existing_template.avatar = temp.avatar
        existing_template.temperature = temp.temperature
        existing_template.model = temp.model
        existing_template.voice_switch = temp.voice_switch
        existing_template.voice_style = temp.voice_style
        existing_template.voice_emotion = temp.voice_emotion
        existing_template.vector_switch = temp.vector_switch
        existing_template.vector_collection = temp.vector_collection
        existing_template.vector_top_k = temp.vector_top_k
        existing_template.few_shot_switch = temp.few_shot_switch
        existing_template.few_shot_content = temp.few_shot_content
        existing_template.prompt = temp.prompt
        existing_template.character_prompt = temp.character_prompt
        session.commit()
        dic = existing_template.model_to_dict()
        session.close()
        return dic
    else:
        raise AIBeingException('template not found, id:%d' % id)

def get_template_by_id(id: int) -> TemplateModel:
    session = Session()
    template = session.query(TemplateModel).filter_by(id=id).first()
    session.close()
    return template

def get_template_list() -> List[TemplateModel]:
    session = Session()
    template_list = session.query(TemplateModel).all()
    session.close()
    return template_list
def create_table():
    # 创建表
    Base.metadata.create_all(engine)

if __name__ == '__main__':
    # create_table()

    x = get_template_by_id(1)
    print(x.name)

    y = get_template_list()
    print(y)