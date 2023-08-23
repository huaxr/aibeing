# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com
from interact.llm.codeinterpreter.session import CodeInterpreterSession, File

def main():
    # context manager for start/stop of the session
    session = CodeInterpreterSession()
    session.start()
    # define the user request
    user_request = "分析数据并生成饼状图"
    files = [
        File.from_path("./assets/iris.csv"),
    ]

    # generate the response
    response = session.generate_response_sync(user_request, files=files)

    # output the response (text + image)
    response.show()


if __name__ == "__main__":
    main()