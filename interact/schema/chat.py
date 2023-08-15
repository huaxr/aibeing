# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com
import json
from interact.schema.protocal import protocol

class response:
    def __init__(self, protocol:protocol=None,  debug =None, style=None, audio_url=None, template_id=None, chat_id=None):
        self.pt = protocol
        self.txt = debug
        self.style = style
        self.audio_url = audio_url
        self.template_id = template_id
        self.chat_id = chat_id
    def __str__(self):
        return self.toStr()

    def toStr(self) -> str:
        res = { "pt": self.pt, "txt": self.txt}
        if self.style != None:
            res["style"] = self.style
        if self.audio_url != None:
            res["audio_url"] = self.audio_url
        if self.template_id != None:
            res["template_id"] = self.template_id
        if self.chat_id != None:
            res["chat_id"] = self.chat_id
        return json.dumps(res)

