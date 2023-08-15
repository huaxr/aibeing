# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com

greeting_template = """Here are some backgrounds for current situation:
Present time: {current_time}
Weather: Sunny
Location: Beijing

Now, Please generate five greetings in Chinese based on the characters below:
<<Character>>
```###```

Your response must be in following JSON format:
```["greeting-1", "greeting-2", "greeting-3", "greeting-4", "greeting-5"]```
"""