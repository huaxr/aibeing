# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com

from flask import Flask, jsonify, request

from core.log import logger

app = Flask(__name__)

@app.route('/set_prompt', methods=['POST', 'GET'])
def get_data():
    print(1111111)
    data = request.get_json()
    prompt  = data["data"]

    return jsonify({"status": "ok"})

def startapp():
    logger.info("start app")
    app.run(host='0.0.0.0', port=8000)
