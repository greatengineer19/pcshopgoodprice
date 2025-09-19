from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
openai_bot_model = os.getenv('OPENAI_BOT_MODEL')
client = OpenAI(api_key=openai_api_key)

class AskChatGPT:
    def build_response(userinput: str) -> str:
        response = client.chat.completions.create(
            model= openai_bot_model,
            messages=[
                {
                    "role": "system", "content": "Limit response to 300 characters. analyze report based on the user input"
                },
                {
                    "role": "user", "content": userinput
                }
            ]
        )

        return response.choices[0].message.content
