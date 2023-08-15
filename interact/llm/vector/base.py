# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com
import os
from core.log import logger

class Vector(object):
    def content_generater(self, folder_path:str, chunk_size:int, overlap_rate:float):
        assert overlap_rate < 1.0 and overlap_rate > 0.0
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".txt"):
                    file_path = os.path.join(root, file)
                    logger.info("load file %s" % file_path)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        start = 0
                        while start < len(content):
                            logger.info("add chunk %s-%s" % (start, start + chunk_size))
                            yield content[start: start + chunk_size]
                            start = start+chunk_size - int((chunk_size * overlap_rate) / 2)



