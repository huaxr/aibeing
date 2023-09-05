# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com
from flask import Flask, request, jsonify

app = Flask(__name__)

# OCR route
@app.route('/ocr', methods=['POST'])
def ocr():
    print("分析图片")
    return jsonify({"result": "hello."})
@app.route('/weather', methods=['POST'])
def weather():
    print("分析天气")
    return jsonify({"result": "good"})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8880)
