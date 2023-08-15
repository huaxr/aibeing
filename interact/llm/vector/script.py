# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com
from interact.llm.vector.client import VectorDB

class ScriptDB(VectorDB):
    def flush_db(self, collection: str, folder_path: str, chunk_size: int, batch_size: int):
        batch = batch_size
        tmp = []
        for i, chunk in enumerate(self.content_generater(folder_path, chunk_size, 0.2)):
            tmp.append(chunk)
            batch-=1
            if batch == 0:
                self.add(collection, tmp)
                tmp = []
                batch = batch_size

def main():
    collection = "mixiaoquan"
    vdb = ScriptDB()
    vdb.delete_collection(collection)
    vdb.create_collection(collection)
    # p = "/Users/huaxinrui/AIB/aibeing/data/mxq"
    p = "/root/aibeing/data/mxq"
    vdb.flush_db(collection, p, 100, 100)
    res = vdb.similarity(collection, "前几天的头脑风暴大赛", 10)
    print(res)
