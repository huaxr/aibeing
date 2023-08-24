# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com

class protocol:
    chat_response = "chat_rsp"
    pong = "pong"
    login = "login"

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

    get_greeting = "get_greeting"
    get_continue_chat = "get_continue_chat"
    pure_chat = "pure_chat"