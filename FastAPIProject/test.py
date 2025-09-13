from openai import OpenAI
from dotenv import load_dotenv
import os
load_dotenv()
api_key = os.environ.get("DEEPSEEK_API_KEY")
client = OpenAI(base_url="https://api.deepseek.com", api_key=api_key)

completion = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {
            "role":"user",
            "content": "你是谁"
        }
    ],
)

print(completion.choices[0].message.content)