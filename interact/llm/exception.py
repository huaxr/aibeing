# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com

class AIBeingException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)