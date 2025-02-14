import os

from groq import Groq
from openai import OpenAI

from backend.vector_search import (
    # vector_search,
    vector_search_light,
)


OPENAI_MODEL = "gpt-4o"
OPENAI_MODEL = "openai-o1"
GROQ_MODEL = "llama-3.3-70b-versatile"

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if GROQ_API_KEY is None:
    raise ValueError("GROQ_API_KEY environment variable is not set")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
if GITHUB_TOKEN is None:
    raise ValueError("GITHUB_TOKEN environment variable is not set")
endpoint = "https://models.inference.ai.azure.com"

openai_client = OpenAI(
    base_url=endpoint,
    api_key=GITHUB_TOKEN,
)
groq_client = Groq(api_key=GROQ_API_KEY)

def get_openai_response(user_input: str) -> str:
    try:
        # 執行向量搜尋並取得結果
        search_result = vector_search(user_input)
        
        # 提取搜尋結果中的 'combined_text'
        combined_text = search_result.get("combined_text", "我們無法找到相關的資料，請詳細說明或重試。")
        # 提取搜尋結果中的 'respondent'
        respondent = search_result.get("respondent", "未知")
        
        # 向 OpenAI 提交請求，並傳遞上下文
        response = openai_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "你是一個說中文的大學學長姐，盡量言簡意賅，不要太長"},
                {"role": "user", "content": "有學生問"+ user_input},
                {"role": "system", "content": "以下是查到的資料"+ combined_text}
                
            ],
            temperature=1.0,
            top_p=1.0,
            max_tokens=1000,
            model=OPENAI_MODEL,
        )
        print(f"Combined:{combined_text}")
        print(f"OpenAI response: {response.choices[0].message.content}")
        
        # 返回 OpenAI 回應內容
        return response.choices[0].message.content, respondent
    except Exception as e:
        # 錯誤處理
        raise RuntimeError(f"Error from OpenAI API: {str(e)}")



def get_groq_response(user_input: str) -> str:
    try:
        search_result = vector_search_light(user_input)
        
        combined_text = search_result.get("combined_text", "我們無法找到相關的資料，請詳細說明或重試。")
        respondent = search_result.get("respondent", "未知")
        
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": "你是一個說中文的大學學長姐，盡量言簡意賅，不要太長"},
                {"role": "user", "content": "有學生問" + user_input},
                {"role": "system", "content": "以下是查到的資料" + combined_text}
            ],
            temperature=1.0,
            top_p=1.0,
            max_tokens=1000
        )
        
        print(f"Combined: {combined_text}")
        print(f"Groq response: {response.choices[0].message.content}")
        
        return response.choices[0].message.content, respondent
    except Exception as e:
        raise RuntimeError(f"Error from Groq API: {str(e)}")

if __name__ == "__main__":
    # get_openai_response("系統分析要注意什麼")
    get_groq_response("系統分析要注意什麼")