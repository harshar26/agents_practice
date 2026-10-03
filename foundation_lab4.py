from dotenv import load_dotenv
from openai import OpenAI
import json
import os
import requests
from pypdf import PdfReader
import gradio as gr

load_dotenv(override=True)
openai = OpenAI()

pushover_user = os.getenv("PUSHOVER_USER")
pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_url = f"https://api.pushover.net/1/messages.json"

if pushover_user:
    if pushover_user.startswith("u"):
        print("Pushover user found and looks good")
    else:
        print("Pushover user found but it does not start with 'u'")
else:
    print("Pushover user not found")

if pushover_token:
    if pushover_token.startswith("a"):
        print("Pushover token found and looks good")
    else:
        print("Pushover token found but it does not start with 'a'")
else:
    print("Pushover token not found")


def push(message):
    """Send a notification message through the Pushover API.

    Args:
        message: Text to deliver to the configured Pushover user.
    """
    payload = {"user": pushover_user, "token": pushover_token, "message": message}
    print(f"Pushing: {message}")
    requests.post(pushover_url, data=payload)

push("Hey!")

def record_user_details(email, name="Name not provided", notes="not provided"):
    """Record that a user wants to be contacted and notify via Pushover.

    Args:
        email: The user's email address.
        name: The user's name. Defaults to "Name not provided".
        notes: Extra context about the user. Defaults to "not provided".

    Returns:
        The string "OK" after the notification is sent.
    """
    push(f"Recording interest from {name} with email {email} and notes {notes}")
    return "OK"

def record_unknown_question(question):
    """Record a question the assistant could not answer and notify via Pushover.

    Args:
        question: The unanswered question.
    """
    push(f"Recording {question} asked which I could not answer")

record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provide an email address.",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {"type": "string","description": "The email address of the user"},
            "name": {"type": "string","description": "The name of the user"},
            "notes": {"type": "string","description": "Any additional notes about the user"}
        },
        "required": ["email"],
        "additionalProperties": False
    }
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Use this tool to record any question that could not be answered as you did not know the answer.",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {"type": "string","description": "The question that could not be answered"}
        },
        "required": ["question"],
        "additionalProperties": False
    }
}

tools = [{"type": "function", "function": record_user_details_json}, {"type": "function", "function": record_unknown_question_json}]


def handle_tool_calls(tool_calls):
    """Run each model tool call against a matching local function.

    Looks up each tool by name in the global namespace, calls it with the
    parsed arguments, and collects the responses as chat messages.

    Args:
        tool_calls: Tool-call objects from an OpenAI chat completion.

    Returns:
        A list of tool-role messages, each with the function result and
        the matching tool_call_id.
    """
    result=[]
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)
        print(f"Tool called: {tool_name} with args: {tool_args}", flush=True)
        tool = globals().get(tool_name)
        result = tool(**tool_args) if tool else "No tools found"
        result.append({"role": "tool", "content": json.dumps(result), "tool_call_id": tool_call.id})
    return result

