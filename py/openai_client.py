import os

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
token = os.environ.get("GITHUB_TOKEN")
if token is None:
    raise ValueError("GITHUB_TOKEN environment variable is not set")

endpoint = "https://models.inference.ai.azure.com"
model_name = "gpt-4o"

client = OpenAI(
    base_url=endpoint,
    api_key=token,
)

def get_openai_response(user_input: str) -> str:
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "你是一個說中文的大學助教"},
                {"role": "user", "content": user_input},
            ],
            temperature=1.0,
            top_p=1.0,
            max_tokens=1000,
            model=model_name,
        )
        return response.choices[0].message.content
    except Exception as e:
        raise RuntimeError(f"Error from OpenAI API: {str(e)}")

# response = client.chat.completions.create(
#     messages=[
#         {
#             "role": "system",
#             "content": "You are a helpful assistant.",
#         },
#         {
#             "role": "user",
#             "content": "Give me 5 good reasons why I should exercise every day.",
#         }
#     ],
#     temperature=1.0,
#     top_p=1.0,
#     max_tokens=1000,
#     model=model_name,
#     stream=True
# )

# print(response.choices[0].message.content)

# for update in response:
#     if update.choices[0].delta.content:
#         print(update.choices[0].delta.content, end="")