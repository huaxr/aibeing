# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com
from interact.handler.voice.microsoft import TTSMS


def main():
    x = TTSMS()

    dict_info = {}
    root = "/Users/huaxinrui/AIB/aibeing/data/aidatatang_200zh/"
    with open(root + 'transcript/aidatatang_200_zh_transcript.txt', "r", encoding="utf-8") as dict_transcript:
        for v in dict_transcript:
            if not v:
                continue
            v = v.strip().replace("\n","").replace("\t"," ").split(" ")
            dict_info[v[0]] = " ".join(v[1:])

    for k, v in dict_info.items():

        success, audio_file = x.text2audio("zh-CN-XiaoxiaoNeural", "cheerful", v.replace(" ", ""), root + "corpus/train/xiaoxiao/xiaoxiao/" + k + ".wav")
        print(success, audio_file)


if __name__ == "__main__":
    main()
