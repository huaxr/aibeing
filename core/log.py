# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com

import logging
import logging.handlers
import json
from .conf import config
class AIBeingLog:
    def __init__(self, log_file, max_bytes, backup_count):
        self.logger = logging.getLogger("AIBeingLogger")
        self.logger.setLevel(logging.INFO)

        # 创建日志处理器
        json_handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
        json_handler.setFormatter(logging.Formatter(json.dumps(self._get_log_format())))

        # 创建终端处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

        self.logger.addHandler(json_handler)
        self.logger.addHandler(console_handler)

    def _get_log_format(self):
        return {
            "timestamp": "%(asctime)s",
            "level": "%(levelname)s",
            "message": "%(message)s"
        }

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

logger: AIBeingLog = AIBeingLog(config.log_path, 1024 * 1024 * 10, 5)
