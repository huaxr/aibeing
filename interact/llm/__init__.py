# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com
from interact.schema.chat import response
from interact.schema.protocal import protocol

def check_running(func):
    def wrapper(self, *args, **kwargs):
        func_flag = func.__name__ + "_flag"
        if not hasattr(self, func_flag):
            setattr(self, func_flag, None)
            try:
                res = func(self, *args, **kwargs)
            finally:
                delattr(self, func_flag)
            return res
        return response(protocol=protocol.exception, debug="请等待输出完毕再输入...".format(func_flag)).toStr()
    return wrapper