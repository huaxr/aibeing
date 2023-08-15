# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com

from typing import Any, Dict, List, Optional, Union
from langchain.schema import AgentAction, AgentFinish
from langchain.callbacks.base import BaseCallbackHandler, AsyncCallbackHandler
from interact.schema.chat import response
from interact.schema.protocal import protocol

class AIBeingHookAsync(AsyncCallbackHandler):
    def __init__(self, sock, template_id: int):
        """Initialize callback handler."""
        self.sock = sock
        self.template_id = template_id
        self.content_format = '"reply":'
        self.current_sentence = ""

    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        self.current_sentence += token

        if token.__contains__("{"):
            await self.sock.send(response(protocol=protocol.stream_start, template_id=self.template_id).toStr())

        if len(token) > 0 and self.current_sentence.__contains__(self.content_format) and not token.__contains__('"') and not token.__contains__("}"):
            await self.sock.send(response(protocol=protocol.stream_action, debug=token, template_id=self.template_id).toStr())

        if token.__contains__("}"):
            self.current_sentence = ""
            await self.sock.send(response(protocol=protocol.stream_end, template_id=self.template_id).toStr())

class AIBeingHook(BaseCallbackHandler):
    """Callback Handler that prints to std out."""
    def __init__(self, queue, template_id):
        """Initialize callback handler."""
        self.q = queue
        self.template_id = template_id
        self.current_sentence = ""
        self.content_format = '"reply":'
    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Print out the prompts."""
        pass

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        # uuid = str(kwargs["run_id"])
        self.current_sentence += token

        if token.__contains__("{"):
            self.q.put(response(protocol=protocol.stream_start, template_id=self.template_id).toStr())

        if len(token) > 0 and self.current_sentence.__contains__(self.content_format) and not token.__contains__('"') and not token.__contains__("}"):
            self.q.put(response(protocol=protocol.stream_action, debug=token, template_id=self.template_id).toStr())

        if token.__contains__("}"):
            self.current_sentence = ""
            self.q.put(response(protocol=protocol.stream_end, template_id=self.template_id).toStr())

        # sys.stdout.write(token)
        # sys.stdout.flush()

    def on_llm_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        """Do nothing."""

    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> None:
        """Print out that we are entering a chain."""
        pass


    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """Print out that we finished a chain."""
        pass

    def on_chain_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        """Do nothing."""

    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        **kwargs: Any,
    ) -> None:
        """Do nothing."""

    def on_agent_action(
        self, action: AgentAction, color: Optional[str] = None, **kwargs: Any
    ) -> Any:
        """Run on agent action."""

    def on_tool_end(
        self,
        output: str,
        color: Optional[str] = None,
        observation_prefix: Optional[str] = None,
        llm_prefix: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Run when tool ends."""

    def on_tool_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        """Do nothing."""

    def on_text(
        self,
        text: str,
        color: Optional[str] = None,
        end: str = "",
        **kwargs: Any,
    ) -> None:
        """Run when agent ends."""
        pass

    def on_agent_finish(
        self, finish: AgentFinish, color: Optional[str] = None, **kwargs: Any
    ) -> None:
        """Run on agent end."""
