import os
from openai import OpenAI
from dotenv import load_dotenv
from vector_search import vector_search

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
        # 執行向量搜尋並取得結果
        search_result = vector_search(user_input)
        
        # 提取搜尋結果中的 'combined_text'
        combined_text = search_result.get("combined_text", "我們無法找到相關的資料，請詳細說明或重試。")
        # 提取搜尋結果中的 'respondent'
        respondent = search_result.get("respondent", "未知")
        
        # 向 OpenAI 提交請求，並傳遞上下文
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "你是一個說中文的大學學長姐，盡量言簡意賅，不要太長"},
                {"role": "user", "content": "有學生問"+ user_input},
                {"role": "system", "content": "以下是查到的資料"+ combined_text}
                
            ],
            temperature=1.0,
            top_p=1.0,
            max_tokens=1000,
            model=model_name,
        )
        print(f"Combined:{combined_text}")
        print(f"OpenAI response: {response.choices[0].message.content}")
        
        # 返回 OpenAI 回應內容
        return response.choices[0].message.content, respondent
    except Exception as e:
        # 錯誤處理
        raise RuntimeError(f"Error from OpenAI API: {str(e)}")


# get_openai_response("系統分析要注意什麼")