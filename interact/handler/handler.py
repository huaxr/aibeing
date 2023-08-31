# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com
import json
from typing import Any, Dict, Optional

from core.conf import config
from interact.handler.base import BaseHandler
from interact.handler.voice.microsoft import AudioTransform
from interact.llm.exception import AIBeingException
from interact.schema.chat import response


class StreamHandler(BaseHandler):
    def __init__(self, audiotrans: AudioTransform=None):
        super().__init__(audiotrans)

    def on_message(self, message) -> (Dict, bool):
        try:
            js = json.loads(message)
        except:
            # when debug locally, the message is plain text, otherwise it is json
            return {"pt": "local"}, False

        pt = js["pt"]

        if pt == "chat_audio":
            file_name = js.get("file_name")
            file = config.audio_upload_path + file_name
            res = self.audiotrans.audio2text(file)
            if len(res.strip()) == 0:
                raise AIBeingException("audio2text failed, try again")
            js["content"] = res
            return js, False

        return self.process(js)

    async def async_on_message(self, message) -> (Dict, bool):
        try:
            js = json.loads(message)
        except:
            return {"pt": "local"}, False

        pt = js["pt"]
        if pt == "chat_audio":
            file_name = js.get("file_name")
            file = config.audio_upload_path + file_name
            res = await self.audiotrans.async_audio2text(file)
            if len(res.strip()) == 0:
                raise AIBeingException("async_audio2text failed, try again")
            js["content"] = res
            return js, False

        return self.process(js)

