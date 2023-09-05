# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com
from typing import Dict

from interact.handler.voice.microsoft import TTSMS
from interact.llm.tasks.base import AIBeingBaseTask
from interact.llm.exception import AIBeingException
from interact.llm.tasks.chat_template import AIBeingChatTask
from interact.llm.tasks.codeinterpreter import AIBeingCotTask
from interact.llm.tasks.chat_pure import AIBeingPureTask
from interact.llm.tasks.gen_story import AIBeingStoryTask
from interact.schema.protocal import protocol

def get_task(js: Dict) -> AIBeingBaseTask:
    pt = js["pt"]
    if pt == protocol.chat_template or pt == protocol.get_greeting:
        session_id = js.get("session_id", None)
        template_id = js.get("template_id", -1)
        assert template_id > 0, "template_id must > 0 when chat_req or get_greeting"
        return AIBeingChatTask(session_id, template_id, TTSMS())

    if pt == protocol.gen_story:
        session_id = js.get("session_id", None)
        return AIBeingStoryTask(session_id)

    if pt == protocol.chat_pure:
        session_id = js.get("session_id", None)
        return AIBeingPureTask(session_id)

    if pt == protocol.chat_thinking:
        return AIBeingCotTask()
    
    raise AIBeingException("pt:{} not supported".format(pt))