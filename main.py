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

if False:
    # Generate a response from the OpenAI API
    response = openai.chat.completions.create(
        model="gpt-5",
        messages=messages
    )
    print(response.choices[0].message.content)

# Ask for a question

question = "Please propose a challenging question to test a person's presence of mind in a difficult situation. Respond only with the question, no other text."

messages = [
    {
        "role": "user",
        "content": question
    }
]

# Print the messages to the console
print(messages)

# Generate a response from the OpenAI API
response = openai.chat.completions.create(model="gpt-5", messages=messages)
question = response.choices[0].message.content
print(question)

# Ask for the answer
messages = [{"role": "user", "content": question}]
response = openai.chat.completions.create(model="gpt-5", messages=messages)
answer = response.choices[0].message.content
print(answer)

# Evaluate the correctness of the answer
message = f"""
Here is a question: 
{question}

And here is a possible answer that be correct or incorrect:
{answer}

Please evaluate the correctness of the answer.

"""

messages = [{"role": "user", "content": message}]
response = openai.chat.completions.create(model="gpt-5", messages=messages)
evaluation = response.choices[0].message.content
print(evaluation)
