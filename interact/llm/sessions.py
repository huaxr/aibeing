# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com
from typing import Optional

from interact.llm.tasks.base import AIBeingBaseTask
from collections import OrderedDict

class SessionCache:
    # LRU
    def __init__(self, maxsize):
        self.maxsize = maxsize
        self.cache = OrderedDict()
    def get(self, key:str) -> Optional[AIBeingBaseTask]:
        if key in self.cache:
            value = self.cache.pop(key)
            self.cache[key] = value
            return value
        return None

    def put(self, key:str, value:AIBeingBaseTask):
        if len(self.cache) >= self.maxsize:
            self.cache.popitem(last=False)
        self.cache[key] = value

sessions = SessionCache(maxsize=100)
