# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com

import yaml
import os
import platform

system = platform.system()
class Config:
    def __init__(self, config_file):
        with open(config_file, 'r') as f:
            config_data = yaml.safe_load(f)
        self.data = config_data

    @property
    def log_path(self) -> str:
        return self.data["log"]["path"]

    @property
    def ws_port(self) -> int:
        return self.data["ws"]["port"]

    @property
    def mysql_dsn(self) -> str:
        return self.data["mysql"]["dsn"]

    @property
    def llm_embedding(self) -> str:
        return self.data["llm"]["embedding"]

    @property
    def llm_type(self) -> str:
        return self.data["llm"]["type"]

    @property
    def llm_async(self) -> bool:
        return self.data["llm"]["async"]

    @property
    def llm_jupyter_port(self) -> int:
        return self.data["llm"]["jupyter_port"]

    @property
    def llm_msai_addr(self) -> str:
        return self.data["llm"]["msai_addr"]

    @property
    def llm_msai_max_token(self) -> int:
        return self.data["llm"]["msai_max_token"]

    @property
    def audio_save_path(self) -> str:
        return self.data["audio"]["save_path"]
    @property
    def audio_upload_path(self) -> str:
        return self.data["audio"]["upload_path"]
    @property
    def image_path(self) -> str:
        return self.data["audio"]["image_path"]

    @property
    def vector_host(self) -> str:
        return self.data["vector"]["host"]
    @property
    def vector_port(self) -> str:
        return self.data["vector"]["port"]

    @property
    def redis_host(self) -> str:
        return self.data["redis"]["host"]
    @property
    def redis_port(self) -> str:
        return self.data["redis"]["port"]
    @property
    def redis_db(self) -> str:
        return self.data["redis"]["db"]


current_dir = os.getcwd()

if system == "Darwin":
    print("Running on Mac OS")
    config: Config = Config(os.path.join(current_dir, "/Users/huaxinrui/AIB/aibeing/conf/local.yml"))
else:
    config: Config = Config(os.path.join(current_dir, "/root/aibeing/conf/config.yml"))


