from dotenv import load_dotenv
import os
from openai import OpenAI


openai_api_key = os.getenv("OPENAI_API_KEY")

if openai_api_key:
    print(f"OpenAI API key starts with: {openai_api_key[:8]}")
else:
    print("OpenAI API key not found")

# Initialize the OpenAI client
openai = OpenAI()

# List of messages in the OpenAI API format
messages = [
    {
        "role": "user",
        "content": "Give me 5 best practices for GitHub version control when working in a team"
    }
]

# Print the messages to the console
print(messages)

# Generate a response from the OpenAI API
response = openai.chat.completions.create(
    model="gpt-5",
    messages=messages
)
print(response.choices[0].message.content)