# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com
import subprocess
from pathlib import Path

from interact.codebox import CodeBox
from interact.llm.exception import AIBeingException

functions = [
    {
        "name": "python",
        "description": "Input a string of code to a ipython interpreter. "
            "Write the entire code in a single string. This string can "
            "be really long, so you can use the `;` character to split lines. "
            "Variables are preserved between runs. ",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "title": "Code",
                },
            },
            "required": ["code"],
        },
    },
]

def python_handler(code):
    try:
        result = subprocess.run(['ipython', '-c', code], check=True, capture_output=True, text=True)
        out = result.stdout
        out = out.replace("Out[1]:", "").strip()
        return out
    except subprocess.CalledProcessError as e:
        return AIBeingException("Error running IPython code: {}".format(e))


def ipython_handler(code):
    box = CodeBox()
    box.start()
    box.run(code)


available_functions = {
    "python": ipython_handler,
}

if __name__ == '__main__':
    code = """
import pandas as pd
import matplotlib.pyplot as plt
# 读取数据
data = pd.read_csv('/tmp/iris.csv')
# 计算每个类别的数量
class_counts = data['class'].value_counts()
# 生成饼状图
plt.figure(figsize=(10, 6))
plt.pie(class_counts, labels=class_counts.index, autopct='%1.1f%%')
plt.title('Iris Classes Distribution')
plt.savefig('/tmp/iris_classes_distribution.png')
print('/tmp/iris_classes_distribution.png')
    """
    res = ipython_handler(code)
    print(res)