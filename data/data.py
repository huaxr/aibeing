# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com
import re


def sanguo_format():
    lines = []
    with open("./sanguo.txt", "r") as file:
        text = file.readlines()

        for i in text:
            if len(i.strip()) == 0 or i.strip().startswith("第") or i.strip().startswith("未发现"):
                continue

            if i.strip().startswith("1") or i.strip().startswith("2") or i.strip().startswith("3") or i.strip().startswith("4") or i.strip().startswith("5") or i.strip().startswith("6") or i.strip().startswith("7") or i.strip().startswith("8") or i.strip().startswith("9"):
                res = i.strip().split("、")
                if len(res) == 2:
                    lines.append(res[1].strip())
            else:
                lines.append(i.strip())

    a = '\n'.join(lines)

    with open("sanguo-format.txt", "w") as new_file:
        new_file.write(a)

if __name__ == '__main__':
    sanguo_format()