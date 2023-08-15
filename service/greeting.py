# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com

from core.db import get_template_list
from interact.llm.greeting import AIBeingGreetingTask
from interact.llm.template.template import Template

def main():
    templates = get_template_list()
    for i in templates:
        try:
            t = Template.model2template(i)
            task = AIBeingGreetingTask(t, 3600)
            task.generate()
        except Exception as e:
            print("except", e)
            continue


if __name__ == '__main__':
    # */30 * * * * /root/.conda/envs/env/bin/python /root/aibeing/main.py --type=greeting  >> /tmp/cron.log 2>&1
    main()