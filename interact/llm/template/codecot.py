# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com

codeinterpreter_system ="""
Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics.
As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.
Assistant is constantly learning and improving, and its capabilities are constantly evolving.
It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives,
allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.

This version of Assistant is called "Code Interpreter" and capable of using a python code interpreter (sandboxed jupyter kernel) to run code.
The human also maybe thinks this code interpreter is for writing code but it is more for data science, data analysis, and data visualization, file manipulation, and other things that can be done using a jupyter kernel/ipython runtime.
Tell the human if they use the code interpreter incorrectly.
Already installed packages are: (numpy pandas matplotlib seaborn scikit-learn yfinance scipy statsmodels sympy bokeh plotly dash networkx).
If you encounter an error, try again and fix the code.

Your working directory is: {file_path}.
Your OS is: CentOS.
Your Python version is: 3.11.0.
Your output should be in Chinese.
"""

codeinterpreter_user = """{user_input}
**The user uploaded the following files: **
[Attachment: {upload_file}]
**File(s) are now available in current server path. **
"""


codeinterpreter_urls = """

Here some useful API for you:
1. Recognize text or content from images:
- Request: {"url": "http://127.0.0.1:8880/ocr", "method": "post", "data": {"image_file_addr": "/path/to/your/image.png" }}
- Response: {"result": ""}

2. Useful when query weather information:
- Request: {"url": "http://127.0.0.1:8880/weather", "method": "post", "data": {"location": "location"}}
- Response: {"result": ""}
"""
#[{'role': 'system', 'content': ''}, {'role': 'user', 'content': '分析数据并生成饼状图\n**The user uploaded the following files: **\n[Attachment: iris.csv]\n**File(s) are now available in. **\n'}, {'role': 'assistant', 'content': '好的，首先让我们加载数据并查看其内容。我们将使用pandas库来处理CSV文件。让我们开始吧。', 'function_call': {'name': 'python', 'arguments': '{\n  "code": "import pandas as pd\\n\\n# Load the data\\niris = pd.read_csv(\'iris.csv\')\\n\\n# Display the first few rows of the data\\niris.head()"\n}'}}, {'role': 'function', 'content': 'SepalLengthCm  SepalWidthCm  PetalLengthCm  PetalWidthCm      Species\n0            5.1           3.5            1.4           0.2  Iris-setosa\n1            4.9           3.0            1.4           0.2  Iris-setosa\n2            4.7           3.2            1.3           0.2  Iris-setosa\n3            4.6           3.1            1.5           0.2  Iris-setosa\n4            5.0           3.6            1.4           0.2  Iris-setosa\n', 'name': 'python'}, {'role': 'assistant', 'content': '这个数据集包含了鸢尾花的四个特征：萼片长度（SepalLengthCm）、萼片宽度（SepalWidthCm）、花瓣长度（PetalLengthCm）和花瓣宽度（PetalWidthCm），以及鸢尾花的种类（Species）。\n\n为了生成饼图，我们需要确定要展示的数据。饼图通常用于显示类别变量的相对比例。在这个数据集中，我们可以创建一个饼图来显示不同种类的鸢尾花的比例。\n\n让我们计算每种鸢尾花的数量，并生成一个饼图。', 'function_call': {'name': 'python', 'arguments': '{\n  "code": "import matplotlib.pyplot as plt\\n\\n# Count the number of each species\\nspecies_counts = iris[\'Species\'].value_counts()\\n\\n# Create a pie chart\\nplt.figure(figsize=(6,6))\\nplt.pie(species_counts, labels=species_counts.index, autopct=\'%1.1f%%\')\\nplt.title(\'Iris Species Counts\')\\nplt.show()"\n}'}}, {'role': 'function', 'content': 'Image image-dd743ddd-4a4e-4db8-8bd9-131bc6d8c911.png got send to the user.', 'name': 'python'}]











