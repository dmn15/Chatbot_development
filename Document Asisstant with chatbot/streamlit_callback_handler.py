import streamlit as st
from langchain.callbacks.base import BaseCallbackHandler
from typing import Any

class StreamlitCallbackHandler(BaseCallbackHandler):
    def __init__(self, container):
        self.container = container
        self.text = ""

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.markdown(self.text)

    def on_llm_end(self, response: Any, **kwargs) -> None:
        self.text = ""  # Reset the text for the next response
