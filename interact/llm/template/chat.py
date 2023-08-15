# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com

chat_template_with_emotion = """
User: {user_input}
Reply: 

1 - Your emotion must be one of: ###. output `emotion`  
2 - When the user speaks Chinese, you reply in Chinese, when the user speaks English, you reply in English, and so on. output `reply`

Your response must be in following JSON format:
```{{"emotion":"You emotion here", "reply":"Your response here"}}```
"""

chat_template_without_emotion = """
User: {user_input}
Reply:

When the user speaks Chinese, you reply in Chinese, when the user speaks English, you reply in English, and so on. output `reply`

Your response must be in following JSON format:
```{{"reply":"Your response here"}}```
"""

introduction_template = "You are a theme chatbot, the following is the introduction of the story theme:\n```{introduction_input}```"
introduction_template_cn = "<<你是一个主题聊天机器人,以下是故事主题>>\n```{introduction_input}```"

corpus_template = "\n\nYou can refer to the following corpus to enrich your answers:\n```{system_input}```"
corpus_template_cn = "\n\n<<当前会话的相关语料库>>\n```{system_input}```"

analyze_template = "\n\nYour goal: to facilitate the conversation:\n```{analyze_input}```"
analyze_template_cn = "\n\n<<你的目标: 促进会话进展>>\n```{analyze_input}```"