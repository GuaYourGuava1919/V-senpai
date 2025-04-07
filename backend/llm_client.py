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
        print(f"向量查詢結果標題: {title}")
        content = search_result.get("content", "未知內容")
        print(f"向量查詢結果內容: {content}")
        
        
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是一位說中文的大學學長姐，專門幫助後輩解答與系統分析與設計課程相關的問題。"
                        "你的回答要有經驗分享的語氣，簡單明確、實用易懂，盡量用口語化的說法，"
                        "並控制在 3～5 句內。"
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"學生的問題是：{user_input}\n\n"
                        f"請根據以下資料來回答這個問題，務必只根據資料內容來推論，不要胡亂補充：\n{content}\n\n"
                        f"這是資料中與問題最相關的重點摘要：{title}"
                    )
                },
            ],
            temperature=0.5,
            top_p=0.9,
            max_tokens=1000
        )


        print(f"Groq API 回應: {response.choices[0].message.content}")
        
        return response.choices[0].message.content, search_result
    except Exception as e:
        raise RuntimeError(f"Error from Groq API: {str(e)}")

if __name__ == "__main__":
    get_groq_response("如何追蹤組員進度")