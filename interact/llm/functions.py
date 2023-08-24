# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com
import subprocess

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
        return result.stdout
    except subprocess.CalledProcessError as e:
        return AIBeingException("Error running IPython code: {}".format(e))


available_functions = {
    "python": python_handler,
}