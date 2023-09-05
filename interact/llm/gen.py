# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com
from typing import Dict

from core.log import logger
from interact.handler.voice.microsoft import TTSMS
from interact.llm.tasks.base import AIBeingBaseTask
from interact.llm.exception import AIBeingException
from interact.llm.tasks.chat_template import AIBeingChatTask
from interact.llm.tasks.codeinterpreter import AIBeingCotTask
from interact.llm.tasks.chat_pure import AIBeingPureTask
from interact.llm.tasks.gen_story import AIBeingStoryTask
from interact.schema.protocal import protocol

def regen_task(task:AIBeingBaseTask, js: Dict, merge= True) -> AIBeingBaseTask:
    pt = js["pt"]
    if task.protocol == pt:
        return task
    if pt == protocol.chat_template or pt == protocol.get_greeting:
        session_id = js.get("session_id", None)
        template_id = js.get("template_id", -1)
        assert template_id > 0, "template_id should be greater than 0"
        t =  AIBeingChatTask(session_id, template_id, TTSMS())

    elif pt == protocol.gen_story:
        t = AIBeingStoryTask()

    elif pt == protocol.chat_pure:
        session_id = js.get("session_id", None)
        t = AIBeingPureTask(session_id)

    elif pt == protocol.chat_thinking:
        t = AIBeingCotTask()
    else:
        raise AIBeingException("unknown protocol:{}".format(pt))
    if merge:
        logger.info("merge task from {} to {} with contexts size:{}".format(task.protocol, pt, len(task.chat_list)))
        context = task.chat_list
        t.chat_list = context
    return t