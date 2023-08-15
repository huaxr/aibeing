# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com

import json
import time

from interact.handler.base import BaseHandler
from interact.handler.voice.bytedace import txt2voice, voice2txt

class AudioHandler(BaseHandler):
    def __init__(self, audio_ext=None, save_path=None):
        super().__init__(audio_ext, save_path)

    def on_message(self, message) -> (str, bool):
        if isinstance(message, bytes):
            return self.audioHandler(message), False
        else:
            # set ext
            js = json.loads(message)
            self.textHandler(js)
            return "", True

    async def async_on_message(self, message) -> (str, int, bool):
        raise NotImplementedError

    def audioHandler(self, message) -> str:
        pt = message[0:2]
        size = message[2:6]
        data = message[6:]
        pt = int.from_bytes(pt, byteorder='little', signed=False)
        size = int.from_bytes(size, byteorder='little', signed=False)

        # 用户上传一段语音
        if pt == 3:
            return self.audio2Text(data, size)
        else:
            return ""

    def textHandler(self, js):
        pt = js["pt"]
        # 设置audio类型,如mp4,opus
        if pt == "set_audio_type_req":
            self.setExt(js)
    def setExt(self, js):
        #保存到文件
        self.audio_ext = js["audio_ext"]

    def audio2Text(self, data, size):
        if self.audio_ext:
            filename = self.save_path + ".".join(["user", str(time.time()), self.audio_ext])
            f = open(filename, "wb")
            f.write(data)
            f.close()
            jsRes = voice2txt(filename)
            if jsRes is not None and len(jsRes['utterances']) > 0:
                return jsRes['utterances'][0]['text']

    def text2Audio(self, txt):
        if self.audio_ext:
            filename = self.save_path + ".".join(["aib", str(time.time()), "mp3"])
            ok, duration = txt2voice(txt, filename)
            if not ok:
                return "", 0
            return filename, duration
        else:
            return "", 0

if __name__ == '__main__':
    file = "test_submit.mp3"
    txt2voice("字节跳动语音合成", file)
    a = voice2txt(file)
    print(a)