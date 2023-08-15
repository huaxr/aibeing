# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com

# 填写平台申请的appid, access_token以及cluster
appid = "5652635987"
access_token= "SBBjrgFw2EgBkNuhR8EqBdW-WxrhtIdD"

# text to voice
cluster = "volcano_tts"

voice_type = "BV700_streaming"
host = "openspeech.bytedance.com"
api_url = f"https://{host}/api/v1/tts"

# voice to text
base_url = 'https://openspeech.bytedance.com/api/v1/vc'
language = 'zh-CN'

import json
import base64
import uuid
import requests
from core.log import logger
def txt2voice(txt, fname) -> (bool, int):
    request_json = {
        "app": {
            "appid": appid,
            "token": "access_token",
            "cluster": cluster
        },
        "user": {
            "uid": "388808087185088"
        },
        "audio": {
            "voice": "other",
            "voice_type": voice_type,
            "encoding": "mp3",
            "speed": 10,
            "volume": 10,
            "pitch": 10,
            "style_name": "story"
        },
        "request": {
            "reqid": str(uuid.uuid4()),
            "text": txt,
            "text_type": "plain",
            "operation": "query",
            "with_frontend": 1,
            "frontend_type": "unitTson"
        }
    }

    try:
        header = {"Authorization": f"Bearer;{access_token}"}
        resp = requests.post(api_url, json.dumps(request_json), headers=header)
        res = resp.json()
        if "data" in res:
            data = res["data"]
            duration = res["addition"]["duration"]
            file_to_save = open(fname, "wb")
            file_to_save.write(base64.b64decode(data))
            return True, duration
    except Exception as e:
        logger.error("err when txt2voice %s" %str(e)[:80])
        return False, 0

#语音转为文件，返回json文本，需要从json里提取出数据
def voice2txt(fpath):
    try:
        fdata = open(fpath, 'rb')
        response = requests.post('{base_url}/submit'.format(base_url=base_url),
                     params = dict(
                         appid=appid,
                         language=language,
                         use_itn='True',
                         dirt_filter='True',
                         use_capitalize='True',
                         max_lines=1,
                         words_per_line=15,
                     ),
                     headers={
                        'content-type': 'audio/opus',
                        'Authorization': 'Bearer; {}'.format(access_token)
                     },
                     data=fdata
                 )
        assert(response.status_code == 200)
        assert(response.json()['message'] == 'Success')

        job_id = response.json()['id']
        response = requests.get(
                '{base_url}/query'.format(base_url=base_url),
                params=dict(
                    appid=appid,
                    id=job_id,
                ),
                headers={
                   'Authorization': 'Bearer; {}'.format(access_token)
                }
        )
        jstr = response.json()
        assert(response.status_code == 200)
        return jstr
    except Exception as e:
        logger.error("err when txt2voice %s" %str(e)[:80])
        return None
