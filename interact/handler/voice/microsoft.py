#!/usr/local/bin/python3
import asyncio
import aiohttp
import aiofiles
import requests
import json
from core.log import logger
from interact.llm.exception import AIBeingException

support_voice_type = [
    "zh-CN-XiaoxiaoNeural",
    "zh-CN-YunxiNeural",
    "zh-CN-YunjianNeural",
    "zh-CN-XiaoyiNeural",
    "zh-CN-YunyangNeural",
    "zh-CN-XiaochenNeural",
    "zh-CN-XiaohanNeural",
    "zh-CN-XiaomengNeural",
    "zh-CN-XiaomoNeural",
    "zh-CN-XiaoqiuNeural",
    "zh-CN-XiaoruiNeural",
    "zh-CN-XiaoshuangNeural",
    "zh-CN-XiaoxuanNeural",
    "zh-CN-XiaoyanNeural",
    "zh-CN-XiaoyouNeural",
    "zh-CN-XiaozhenNeural",
    "zh-CN-YunfengNeural",
    "zh-CN-YunhaoNeural",
    "zh-CN-YunxiaNeural",
    "zh-CN-YunyeNeural",
    "zh-CN-YunzeNeural",
    "zh-CN-henan-YundengNeural",
    "zh-CN-liaoning-XiaobeiNeural",
    "zh-CN-shaanxi-XiaoniNeural",
    "zh-CN-shandong-YunxiangNeural",
    "zh-CN-sichuan-YunxiNeural"
]

support_voice_emotion = ['advertisement_upbeat', 'affectionate', 'angry', 'assistant', 'calm',
                         'chat', 'cheerful', 'customerservice', 'depressed', 'disgruntled', 'documentary-narration',
                         'embarrassed', 'empathetic', 'envious', 'excited', 'fearful', 'friendly', 'gentle', 'hopeful',
                         'lyrical', 'narration-professional', 'narration-relaxed', 'newscast', 'newscast-casual',
                         'newscast-formal', 'poetry-reading', 'sad', 'serious', 'shouting', 'sports_commentary',
                         'sports_commentary_excited', 'whispering', 'terrified', 'unfriendly', "default"]

class AudioTransform(object):
    def __init__(self, save_path: str):
        # self.subscription_key = '9bb20e5cc41f461fb14d8cf90abe5f0b'
        # self.region = 'eastasia'
        self.subscription_key = '4d8a5649051644cca86c5bfea4370286'
        self.region = 'eastasia'
        self.save_path = save_path

    def get_token(self, subscription_key):
        fetch_token_url = f'https://{self.region}.api.cognitive.microsoft.com/sts/v1.0/issueToken'
        headers = {
            'Ocp-Apim-Subscription-Key': subscription_key
        }
        response = requests.post(fetch_token_url, headers=headers)
        access_token = str(response.text)
        return access_token

    #out_file: output.mp3
    def text2audio(self, voice_name, style, text, out_file):
        token = self.get_token(self.subscription_key)
        # Configure the request headers
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/ssml+xml',
            'X-Microsoft-OutputFormat': 'audio-16khz-32kbitrate-mono-mp3',
            'User-Agent': 'web'
        }

        ssml = f"""
        <speak xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xmlns:emo="http://www.w3.org/2009/10/emotionml" version="1.0" xml:lang="zh-CN">
            <voice name="{voice_name}">
                <mstts:express-as style="{style}" styledegree="2"> {text} </mstts:express-as>
            </voice>
        </speak>
        """

        ssml = ssml.encode('utf-8')

        # Send the request to the Text-to-Speech API
        text_to_speech_url = f'https://{self.region}.tts.speech.microsoft.com/cognitiveservices/v1'
        response = requests.post(text_to_speech_url, headers=headers, data=ssml)

        if response.status_code == 200:
    #        audio_file = 'output.mp3'
            audio_file = out_file
            with open(audio_file, 'wb') as f:
                f.write(response.content)
            return True, audio_file
        else:
            raise AIBeingException(f'Error text2audio: {response.status_code}, {response.text},' + token)


    async def async_get_token(self, subscription_key, region):
        fetch_token_url = f'https://{region}.api.cognitive.microsoft.com/sts/v1.0/issueToken'
        headers = {
            'Ocp-Apim-Subscription-Key': subscription_key
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(fetch_token_url, headers=headers) as response:
                access_token = await response.text()
                return access_token

    async def async_text2audio(self, voice_name, style, text, out_file):
        token = await self.async_get_token(self.subscription_key, self.region)

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/ssml+xml',
            'X-Microsoft-OutputFormat': 'audio-16khz-32kbitrate-mono-mp3',
            'User-Agent': 'web'
        }

        ssml = f"""
        <speak xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xmlns:emo="http://www.w3.org/2009/10/emotionml" version="1.0" xml:lang="zh-CN">
            <voice name="{voice_name}">
                <mstts:express-as style="{style}" styledegree="2"> {text} </mstts:express-as>
            </voice>
        </speak>
        """

        ssml = ssml.encode('utf-8')

        text_to_speech_url = f'https://{self.region}.tts.speech.microsoft.com/cognitiveservices/v1'

        async with aiohttp.ClientSession() as session:
            async with session.post(text_to_speech_url, headers=headers, data=ssml) as response:
                if response.status == 200:
                    audio_file = out_file
                    async with aiofiles.open(audio_file, 'wb') as f:
                        await f.write(await response.read())
                    return True, audio_file
                else:
                    raise AIBeingException(f'Error text2audio: {response.status}, {await response.text()},' + token)

        return False, None

    # 只支持ogg, wav格式
    def audio2text(self, mp3: str) -> str:
        url = "https://{}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1?language=zh-CN".format(self.region)

        headers = {
            'Content-type': 'audio/wav;codec="audio/pcm";',
            'Ocp-Apim-Subscription-Key': self.subscription_key,
        }

        with open(mp3, 'rb') as payload:
            response = requests.request("POST", url, headers=headers, data=payload)
            jobj = json.loads(response.text)
            return jobj["DisplayText"]

    async def async_audio2text(self, mp3: str) -> str:
        url = "https://{}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1?language=zh-CN".format(self.region)
        headers = {
            'Content-type': 'audio/wav;codec="audio/pcm";',
            'Ocp-Apim-Subscription-Key': self.subscription_key,
        }

        async with aiohttp.ClientSession() as session:
            with open(mp3, 'rb') as payload:
                async with session.post(url, headers=headers, data=payload) as response:
                    jobj = json.loads(await response.text())
                    return jobj["DisplayText"]
async def main():
    # Define the required parameters
    voice_name = 'zh-CN-XiaoxiaoNeural'
    style = "chat"
    text = "你好,这是一段中文，我还是说中文好听吧"
    out_file = "output.mp3"
    x = AudioTransform(save_path="/tmp")
    # Call ms_tts_async with await
    success, audio_file = await x.async_text2audio(voice_name, style, text, out_file)

    # Check if the operation was successful
    if success:
        print(f'The audio file "{audio_file}" has been saved.')
    else:
        print("Error occurred during TTS operation.")

if __name__ == "__main__":
    asyncio.run(main())
