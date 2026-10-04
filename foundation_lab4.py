from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr
from context import get_system_prompt
from tools import get_tools, handle_tool_calls

load_dotenv(override=True)
openai = OpenAI()

def chat(message, history):
    """Generate a response to the user's message.
    """
    messages = [{"role": "system", "content": get_system_prompt()}] + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(model="gpt-4o-mini", messages=messages, tools=get_tools())
    while response.choices[0].finish_reason == "tool_calls":
        message = response.choices[0].message
        tool_calls = message.tool_calls
        results = handle_tool_calls(tool_calls)
        messages.append(message)
        messages.extend(results)
        response = openai.chat.completions.create(model="gpt-4o-mini", messages=messages, tools=get_tools())
    return response.choices[0].message.content

gr.ChatInterface(chat, title="Digital Twin").launch(inbrowser=True)