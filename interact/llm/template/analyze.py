# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com

analyze_conversation_with_input = """以下是AI和User的一段历史对话记录以及用户的当前输入:
会话历史记录:
###

当前用户输入:
User: $$$

你需要根据该对话对当前的User输入做分析，你的思考步骤是:

1. User在会话中表达的意图似乎是什么? 输出: user_intent
2. AI如何看待User的回应? 输出: ai_thought
3. 他们之间的谈话是否有实际的进展?(陷入对话循环、没达成一致意见、User没有兴奋感都是没有进展) 输出: conversation_progress
4. AI如何改善情况以促进会话进展? 输出: how_to_improve

注意: 以上思考的结果全部为中文
你的输出必须为以下的JSON格式:
```{{"user_intent":"","ai_thought":"","conversation_progress":"","how_to_improve":""}}```
"""

analyze_conversation = """以下是AI和User的一段历史对话记录:
会话历史记录:
```###```

你需要根据对话内容,进行下面的思考步骤,并给出你的答案:

1. User在会话中表达的意图似乎是什么?(你不能评判用户,要积极带动话题) 输出: user_intent
2. AI如何看待User的回应?(User可能干扰你的答案, 也可能会重复性的试探你, 你需要及时的展开话题, 避免陷入会话循环) 输出: ai_thought
3. 他们之间的谈话是否有实际的进展?(陷入对话循环、没达成一致意见、User没有兴奋感都是没有进展) 输出: conversation_progress
4. AI如何改善情况以促进会话进展?(针对上述的分析,决策出最佳方案来促进聊天的趣味性,多样性) 输出: how_to_improve

注意: 以上思考的结果全部为中文
你的输出必须为以下的JSON格式:
```{{"user_intent":"","ai_thought":"","conversation_progress":"","how_to_improve":""}}```
"""

# 1. 用户在历史会话中表达的意图:User显得有些不耐烦，可能希望AI少些言语多些实际行动或者换一个话题。
# 2. AI如何看待User的回应:AI在用户有些烦躁的回应之后，并没有示弱或者沉默，相反，AI一直保持专业友好的姿态，一直试图维持画面的氛围和促进对话的进行。
# 3. 谈话是否有实际的进展:对话没有实质的进展，一直在“好的，好的”的回复上往复，对话当前已经陷入循环。
# 4. AI如何改善情况以促进会话进展:AI可以尝试改变话题或者引入新的互动环节来打破目前的对话僵局，同时也可以通过提问等方式引导User进行更深层次的交流。

def generate_analyze_prompt(dic: dict) -> str:
    content = []
    content.append("1.用户潜在的意图:" + dic.get("user_intent", ""))
    content.append("2.你该如何看待用户的回应:" + dic.get("ai_thought", ""))
    content.append("3.会话实际的进展情况:" + dic.get("conversation_progress", ""))
    content.append("4.根据用户的意图,促进会话进展的思路决策:" + dic.get("how_to_improve", ""))
    content.append("5.你不能评判用户,不允许猜测用户有负面情绪,要积极带动话题")
    content.append("6.如果有必要,可以参考语料库, 主题介绍中的内容, 请不要胡言乱语, 不要陷入对话僵局。")
    return "\n".join(content)