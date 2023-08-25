# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com
from core.log import logger


class AIBeingException(Exception):
    def __init__(self, message):
        self.message = message
        logger.error(self.message)
        super().__init__(self.message)