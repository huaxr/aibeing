# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com

from typing import Optional
from langchain.chains.openai_functions import (
    create_openai_fn_chain,
)
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

# If we pass in a model explicitly, we need to make sure it supports the OpenAI function-calling API.
llm = ChatOpenAI(model="gpt-4", temperature=0)

class RecordPerson(BaseModel):
    """Record some identifying information about a pe."""

    name: str = Field(..., description="The person's name")
    age: int = Field(..., description="The person's age")
    fav_food: Optional[str] = Field(None, description="The person's favorite food")


class RecordDog(BaseModel):
    """Record some identifying information about a dog."""

    name: str = Field(..., description="The dog's name")
    color: str = Field(..., description="The dog's color")
    fav_food: Optional[str] = Field(None, description="The dog's favorite food")

prompt_msgs = [
    SystemMessage(content="You are a world class algorithm for recording entities"),
    HumanMessage(
        content="Make calls to the relevant function to record the entities in the following input:"
    ),
    HumanMessagePromptTemplate.from_template("{input}"),
    HumanMessage(content="Tips: Make sure to answer in the correct format"),
]
prompt = ChatPromptTemplate(messages=prompt_msgs)


# call openai  functions parameters
# [{'name': 'RecordPerson', 'description': 'Record some identifying information about a pe.', 'parameters': {'title': 'RecordPerson', 'description': 'Record some identifying information about a pe.', 'type': 'object', 'properties': {'name': {'title': 'Name', 'description': "The person's name", 'type': 'string'}, 'age': {'title': 'Age', 'description': "The person's age", 'type': 'integer'}, 'fav_food': {'title': 'Fav Food', 'description': "The person's favorite food", 'type': 'string'}}, 'required': ['name', 'age']}}, {'name': 'RecordDog', 'description': 'Record some identifying information about a dog.', 'parameters': {'title': 'RecordDog', 'description': 'Record some identifying information about a dog.', 'type': 'object', 'properties': {'name': {'title': 'Name', 'description': "The dog's name", 'type': 'string'}, 'color': {'title': 'Color', 'description': "The dog's color", 'type': 'string'}, 'fav_food': {'title': 'Fav Food', 'description': "The dog's favorite food", 'type': 'string'}}, 'required': ['name', 'color']}}]


chain = create_openai_fn_chain([RecordPerson, RecordDog], llm, prompt, verbose=True)
a = chain.run("Harry was a chubby brown beagle who loved chicken")

print(a)  # type(a) is RecordDog