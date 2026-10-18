import os
import requests
import asyncio
from dotenv import load_dotenv
from openai.types.responses import ResponseTextDeltaEvent
from agents import Agent, Runner, trace, function_tool, SQLiteSession


load_dotenv(override=True)

pushover_user = os.getenv("PUSHOVER_USER")
pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_url = "https://api.pushover.net/1/messages.json"

if pushover_user:
    if pushover_user.startswith("u"):
        print("Pushover user found and looks good")
    else:
        print("Pushover user found but doesn't start with u")
else:
    print("Pushover user not found")

if pushover_token:
    if pushover_token.startswith("a"):
        print("Pushover token found and looks good")
    else:
        print("Pushover token found but doesn't start with a")
else:
    print("Pushover token not found")



@function_tool
def push_tool(message: str) -> str:
    """ Send the given message to the user as a push notification """
    payload = {
        "token": pushover_token,
        "user": pushover_user,
        "message": message
    }
    result = requests.post(pushover_url, data=payload).status_code
    return f"Push sent with API status code: {result}"


notifier = Agent(name="Notifier", instructions="You notify the user upon request", model="gpt-4o-mini", tools=[push_tool])


async def main():
    with trace("Pizza has arrived"):
        result = await Runner.run(notifier, "Notify the user that pizza has arrived")
    print(result.final_output)



if __name__ == "__main__":
    asyncio.run(main())