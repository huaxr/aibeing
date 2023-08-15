# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com

import numpy as np

speaker = "zh_speaker_1"

# 加载 .npy 文件为 Numpy 数组
coarse_prompt = np.load(speaker + "_coarse_prompt.npy")
fine_prompt = np.load(speaker + "_fine_prompt.npy")
semantic_prompt = np.load(speaker +"_semantic_prompt.npy")

# 使用 savez 函数将多个数组保存为 .npz 文件，并为每个数组指定对应的键
np.savez(speaker + ".npz",
         semantic_prompt=semantic_prompt,
         coarse_prompt=coarse_prompt,
         fine_prompt=fine_prompt)