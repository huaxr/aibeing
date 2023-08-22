# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com

m = "/home/ops/models/huggingface.co/suno/bark"

from transformers import AutoProcessor, BarkModel
import scipy
processor = AutoProcessor.from_pretrained(m)
model = BarkModel.from_pretrained(m)

x = "/home/ops/models/huggingface.co/suno/bark/speaker_embeddings/v2"
voice_preset = x + "/zh_speaker_9"

xx = """大家好 我是机甲刘备 [music] 除了叽叽歪歪啥都不懂"""
inputs = processor(xx, voice_preset=voice_preset)

audio_array = model.generate(**inputs)
audio_array = audio_array.cpu().numpy().squeeze()



sample_rate = model.generation_config.sample_rate
f = "bark_out_{}.wav".format(11)
scipy.io.wavfile.write(f, rate=sample_rate, data=audio_array)
print(f)