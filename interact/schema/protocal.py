# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com

class protocol:
    chat_response = "chat_rsp"
    pong = "pong"


    stream_start = "stream_start"
    stream_action = "stream_action"
    stream_end = "stream_end"
    exception = "exception"

    create_template_rsp = "create_template_rsp"
    update_template_rsp = "update_template_rsp"
    get_template_by_id_rsp = "get_template_by_id_rsp"
    get_template_list_rsp = "get_template_list_rsp"
    get_greeting_rsp = "get_greeting_rsp"
    get_continue_chat_rsp = "get_continue_chat_rsp"
    flush_cache_rsp = "flush_cache_rsp"

    like = "like"
    unlike = "unlike"
    login = "login"


    thinking_now = "thinking_now"
    thinking_error = "thinking_error"
    thinking_image = "thinking_image"
    thinking_stop = "thinking_stop"

    gen_story_start = "gen_story_start"
    gen_story_action = "chat_rsp"
    gen_story_end = "gen_story_end"

    gen_story = "gen_story"
    chat_thinking = "chat_thinking"
    chat_text, chat_pure = "chat_req", "chat_req"
    chat_audio = "chat_audio"
    get_greeting = "get_greeting"


