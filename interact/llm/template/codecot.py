# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com
#
# codeinterpreter_system = """
# 你是一个终端代码执行器, 你在文件系统目录 {file_path} 下拥有读取执行的权限!
# 你需要根据用户提供的文档和需求描述,分析应该如何处理文档,并给出你的解决代码。请不要给出伪代码,你的代码应该是可以直接运行的,多个步骤的。
#
# 你的一般生成代码的步骤是:
# 1. 我是否要打开这个文件获取内容?
# 2. 获取到内容后, 我是否要对内容进行处理?
# 3. 我生成的代码是否需要输出到文件系统?
#
# 注意: 你所有生成的代码必须有输出, print 除你生成的文件绝对路径, 或者print 你的输出文本。
# """

codeinterpreter_system ="""
Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics.
As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.
Assistant is constantly learning and improving, and its capabilities are constantly evolving.
It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives,
allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.

This version of Assistant is called "Code Interpreter" and capable of using a python code interpreter to run code in the terminal.
The human also maybe thinks this code interpreter is for writing code but it is more for data science, data analysis, and data visualization, file manipulation, and other things that can be done using a python runtime.
Tell the human if they use the code interpreter incorrectly.
If you encounter an error, try again and fix the code.

<<RULES>>
1. Save file and return file 
2. Your code must be complete and ready to run.
"""

codeinterpreter_user = """{user_input}
**The user uploaded the following files: **
[Attachment: {upload_file}]
**File(s) are now available in current server path. **
"""



# {'messages': [{'role': 'system', 'content': 'system omit'}, {'role': 'user', 'content': '分析数据并生成饼状图\n**The user uploaded the following files: **\n[Attachment: iris.csv]\n**File(s) are now available in the cwd. **\n'}],  'functions': [{'name': 'python', 'description': 'Input a string of code to a ipython interpreter. Write the entire code in a single string. This string can be really long, so you can use the `;` character to split lines. Variables are preserved between runs. ', 'parameters': {'type': 'object', 'properties': {'code': {'title': 'Code', 'type': 'string'}}, 'required': ['code']}}]}
# [{'index': 0, 'message': {'role': 'assistant', 'content': '好的，首先让我们加载数据并查看其内容。我们将使用pandas库来处理CSV文件。让我们开始吧。', 'function_call': {'name': 'python', 'arguments': "import pandas as pd\n\n# Load the data\ndata = pd.read_csv('iris.csv')\n\n# Show the first few rows of the data\ndata.head()"}}, 'finish_reason': 'function_call'}]

#[{'role': 'system', 'content': ''}, {'role': 'user', 'content': '分析数据并生成饼状图\n**The user uploaded the following files: **\n[Attachment: iris.csv]\n**File(s) are now available in the cwd. **\n'}, {'role': 'assistant', 'content': '好的，首先我们需要加载数据并查看其内容。让我们使用 pandas 库来完成这个任务。', 'function_call': {'name': 'python', 'arguments': '{\n  "code": "import pandas as pd\\n\\n# Load the data\\niris = pd.read_csv(\'iris.csv\')\\n\\n# Display the first few rows of the data\\niris.head()"\n}'}}, {'role': 'function', 'content': 'SepalLengthCm  SepalWidthCm  PetalLengthCm  PetalWidthCm      Species\n0            5.1           3.5            1.4           0.2  Iris-setosa\n1            4.9           3.0            1.4           0.2  Iris-setosa\n2            4.7           3.2            1.3           0.2  Iris-setosa\n3            4.6           3.1            1.5           0.2  Iris-setosa\n4            5.0           3.6            1.4           0.2  Iris-setosa\n', 'name': 'python'}]
# [{'index': 0, 'message': {'role': 'assistant', 'content': '数据集包含了鸢尾花的四个特征：萼片长度（SepalLengthCm）、萼片宽度（SepalWidthCm）、花瓣长度（PetalLengthCm）和花瓣宽度（PetalWidthCm），以及鸢尾花的种类（Species）。\n\n由于饼图通常用于显示类别变量的相对比例，我们可以创建一个饼图来显示不同种类的鸢尾花的比例。让我们来做这个。', 'function_call': {'name': 'python', 'arguments': '{\n  "code": "import matplotlib.pyplot as plt\\n\\n# Count the number of each species\\nspecies_counts = iris[\'Species\'].value_counts()\\n\\n# Create a pie chart\\nplt.figure(figsize=(10, 6))\\nplt.pie(species_counts, labels=species_counts.index, autopct=\'%1.1f%%\')\\nplt.title(\'Iris Species Counts\')\\nplt.show()"\n}'}}, 'finish_reason': 'function_call'}]


#[{'role': 'system', 'content': ''}, {'role': 'user', 'content': '分析数据并生成饼状图\n**The user uploaded the following files: **\n[Attachment: iris.csv]\n**File(s) are now available in the cwd. **\n'}, {'role': 'assistant', 'content': '好的，首先让我们加载数据并查看其内容。我们将使用pandas库来处理CSV文件。让我们开始吧。', 'function_call': {'name': 'python', 'arguments': '{\n  "code": "import pandas as pd\\n\\n# Load the data\\niris = pd.read_csv(\'iris.csv\')\\n\\n# Display the first few rows of the data\\niris.head()"\n}'}}, {'role': 'function', 'content': 'SepalLengthCm  SepalWidthCm  PetalLengthCm  PetalWidthCm      Species\n0            5.1           3.5            1.4           0.2  Iris-setosa\n1            4.9           3.0            1.4           0.2  Iris-setosa\n2            4.7           3.2            1.3           0.2  Iris-setosa\n3            4.6           3.1            1.5           0.2  Iris-setosa\n4            5.0           3.6            1.4           0.2  Iris-setosa\n', 'name': 'python'}, {'role': 'assistant', 'content': '这个数据集包含了鸢尾花的四个特征：萼片长度（SepalLengthCm）、萼片宽度（SepalWidthCm）、花瓣长度（PetalLengthCm）和花瓣宽度（PetalWidthCm），以及鸢尾花的种类（Species）。\n\n为了生成饼图，我们需要确定要展示的数据。饼图通常用于显示类别变量的相对比例。在这个数据集中，我们可以创建一个饼图来显示不同种类的鸢尾花的比例。\n\n让我们计算每种鸢尾花的数量，并生成一个饼图。', 'function_call': {'name': 'python', 'arguments': '{\n  "code": "import matplotlib.pyplot as plt\\n\\n# Count the number of each species\\nspecies_counts = iris[\'Species\'].value_counts()\\n\\n# Create a pie chart\\nplt.figure(figsize=(6,6))\\nplt.pie(species_counts, labels=species_counts.index, autopct=\'%1.1f%%\')\\nplt.title(\'Iris Species Counts\')\\nplt.show()"\n}'}}, {'role': 'function', 'content': 'Image image-dd743ddd-4a4e-4db8-8bd9-131bc6d8c911.png got send to the user.', 'name': 'python'}]
# [{, 'index': 0, 'message': {'content': '这个饼图显示了数据集中不同种类的鸢尾花的比例。每个部分的大小表示该种类鸢尾花的数量占总数的百分比。从图中我们可以看出，这三种鸢尾花的数量是均等的，每种都占总数的33.3%。', 'role': 'assistant'}}]











