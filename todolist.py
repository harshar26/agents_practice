from dotenv import load_dotenv
from openai import OpenAI
from rich.console import Console
import json


load_dotenv(override=True)

openai = OpenAI()

checklist = []
completed = []


def show(text : str):
    try:
        Console().print(text)
    except Exception:
        print(text)


def get_checklist_report() -> str:
    result = ""
    for index, item in enumerate(checklist):
        if completed[index]:
            result += f"Checklist #{index + 1}: [green][strike]{item}[/strike][/green]\n"
        else:
            result += f"Checklist #{index + 1}: {item}\n"
    show(result)
    return result


def create_checklist(descriptions: list[str]) -> str:
    checklist.extend(descriptions)
    completed.extend([False] * len(descriptions))
    return get_checklist_report()


def mark_complete(index: int, completion_notes: str) -> str:
    if 1 <= index < len(checklist):
        completed[index - 1] = True
    else:
        return "No checklist at this index"
    Console().print(completion_notes)
    return get_checklist_report()


create_checklist_json = {
    "name": "create_checklist",
    "description": "Add new checklist from a list of descriptions and return the full list",
    "parameters": {
        "type": "object",
        "properties": {
            "descriptions": {
                'type': 'array',
                'items': {'type': 'string'},
                'title': 'Descriptions of checklist items'
                }
            },
        "required": ["descriptions"],
        "additionalProperties": False
    }
}

mark_complete_json = {
    "name": "mark_complete",
    "description": "Mark complete the checklist item at the given position (starting from 1) and return the full list",
    "parameters": {
        'properties': {
            'index': {
                'description': 'The 1-based index of the checklist item to mark as complete',
                'title': 'Index',
                'type': 'integer'
                },
            'completion_notes': {
                'description': 'Notes about how you completed the checklist item in rich console markup',
                'title': 'Completion Notes',
                'type': 'string'
                }
            },
        'required': ['index', 'completion_notes'],
        'type': 'object',
        'additionalProperties': False
    }
}

tools = [{
    "type": "function",
    "function": create_checklist_json,
    "description": "Create a new checklist from a list of descriptions"
}, {
    "type": "function",
    "function": mark_complete_json,
    "description": "Mark a checklist item as complete"
}]


def handle_tool_calls(tool_calls):
    results = []
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)
        tool = globals().get(tool_name)
        result = tool(**tool_args) if tool else {}
        results.append({"role": "tool", "content": json.dumps(result), "tool_call_id": tool_call.id})
    return results


def loop(messages):
    response = openai.chat.completions.create(model="gpt-4o-mini", messages=messages, tools=tools)
    while response.choices[0].finish_reason == "tool_calls":
        message = response.choices[0].message
        print(f"message: {message}\n\n")
        tool_calls = message.tool_calls
        print(f"tool_calls: {tool_calls}\n\n")
        results = handle_tool_calls(tool_calls)
        messages.append(message)
        messages.extend(results)
        print(f"messages: {messages}\n\n")
        response = openai.chat.completions.create(model="gpt-4o-mini", messages=messages, tools=tools)
        message = response.choices[0].message
        print(f"message: {message}\n\n")
    show(response.choices[0].message.content)

system_message = """
You are given a problem to solve, by using your checklist tools to plan a list of steps, then carrying out each step in turn.
Now create a plan, set the checklist, carry out the steps, and reply with the solution.
If any quantity isn't provided in the question, then include a step to come up with a reasonable estimate.
Provide your solution in Rich console markup without code blocks.
Do not ask the user questions or clarification; respond only with the answer after using your tools.
"""
user_message = """"
A train leaves Jaipur at 2:00 pm traveling 60 mph.
Another train leaves Delhi at 3:00 pm traveling 80 mph toward Jaipur.
When do they meet?
"""

messages = [{"role": "system", "content": system_message}, {"role": "user", "content": user_message}]
loop(messages)