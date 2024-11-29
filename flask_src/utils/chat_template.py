from flask_src.definitions.definitions import MessageType
from typing import List

def convert_to_chat_template(messages: List[MessageType]) -> str:
    chat_template = ""
    for message in messages:
        if "user" in message:
            chat_template += f"User: {message['user']}\n"
        elif "assistant" in message:
            chat_template += f"Assistant: {message['assistant']}\n"
    return chat_template