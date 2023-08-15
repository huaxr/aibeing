# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com
# Ensure that CUDA is available and set up for GPU usage
import uuid

import torch
import scipy.io.wavfile
from transformers import AutoProcessor, BarkModel
from flask import Flask, request, jsonify

app = Flask(__name__)

# 定义模型和处理器路径
m = "/home/ops/models/huggingface.co/suno/bark"
x = "/home/ops/models/huggingface.co/suno/bark/speaker_embeddings/v2"
voice_preset = x + "/en_speaker_6"

# 初始化模型和处理器
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
processor = AutoProcessor.from_pretrained(m)
model = BarkModel.from_pretrained(m)
model.to(device)

# 定义处理 POST 请求的路由
@app.route('/generate', methods=['POST'])
def generate_audio():
    data = request.json  # 获取POST请求的JSON数据
    xx = data['text']  # 从JSON数据中获取文本内容

    inputs = processor(xx, voice_preset=voice_preset)
    inputs = {key: value.to(device) for key, value in inputs.items()}
    audio_array = model.generate(**inputs)
    audio_array = audio_array.cpu().numpy().squeeze()

    sample_rate = model.generation_config.sample_rate
    f = "bark_out_{}.wav".format(uuid.uuid4())
    scipy.io.wavfile.write("/tmp/"+f, rate=sample_rate, data=audio_array)
    return jsonify({'file': f})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
