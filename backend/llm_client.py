import os
from groq import Groq

# deploy開
from backend.vector_search import (
    vector_search_light,
)

#local開
# from vector_search import (
#     vector_search_light,
# )

# 環境變數設定
GROQ_MODEL = "llama-3.3-70b-versatile"
# GROQ_MODEL = "qwen-qwq-32b"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY)


def get_groq_response(user_input: str) -> str:
    try:
        search_result = vector_search_light(user_input)
        # print(f"向量查詢結果: {search_result}")
        
        title = search_result.get("title", "未知標題")
        content = search_result.get("content", "未知內容")
        
        
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": "你是一位說中文的大學學長姐，專門回答系統分析課程相關問題，盡量言簡意賅，回答不超過 3-5 句。"},
                {"role": "user", "content": f"學生的問題是：{user_input}\n\n請根據以下資料回答：\n{content}，\n\n這是與資料相關的重點：{title}"},
            ],
            temperature=0.5,  # 降低隨機性
            top_p=0.9,        # 讓回應更集中
            max_tokens=1000
        )

        print(f"Groq API 回應: {response.choices[0].message.content}")
        
        return response.choices[0].message.content, search_result
    except Exception as e:
        raise RuntimeError(f"Error from Groq API: {str(e)}")

if __name__ == "__main__":
    get_groq_response("如何追蹤組員進度")