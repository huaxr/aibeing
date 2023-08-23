# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com
import json
import sys
from io import StringIO

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

from contextlib import redirect_stdout
from contextlib import redirect_stdout
from IPython import get_ipython

def execute_code(code):
    ipython = get_ipython()

    try:
        exec(code)
    finally:
        ipython.magic("capture stop")

    output_result = ipython.last_execution_result.capture.output
    return "\n".join(output_result)


def python_handler(code: str):
    output = execute_code(code)
    return output



available_functions = {
    "python": python_handler,
}  # only one function in this example, but you can have multiple