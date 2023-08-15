# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com
import json
from core.conf import config
from interact.handler.base import BaseHandler
from interact.handler.voice.microsoft import AudioTransform
from interact.llm.exception import AIBeingException


class StreamHandler(BaseHandler):
    def __init__(self, audiotrans: AudioTransform=None):
        super().__init__(audiotrans)

    def on_message(self, message) -> (str, int, bool):
        try:
            js = json.loads(message)
        except:
            # when debug locally, the message is plain text, otherwise it is json
            return message, 1, False

        pt = js["pt"]

        if pt == "chat_audio":
            file = config.audio_upload_path + js["txt"]
            res = self.audiotrans.audio2text(file)
            if len(res.strip()) == 0:
                raise AIBeingException("audio2text failed, try again")
            return res, int(js["template_id"]), False

        return self.process(js)

    async def async_on_message(self, message) -> (str, int, bool):
        try:
            js = json.loads(message)
        except:
            # when debug locally, the message is plain text, otherwise it is json
            return message, 1, False

        pt = js["pt"]
        if pt == "chat_audio":
            file = config.audio_upload_path + js["txt"]
            res = await self.audiotrans.async_audio2text(file)
            if len(res.strip()) == 0:
                raise AIBeingException("async_audio2text failed, try again")
            return res, int(js["template_id"]), False

        return self.process(js)

