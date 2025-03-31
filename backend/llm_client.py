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
        
        question = search_result.get("question", "未知問項")
        answer = search_result.get("answer", "未知答案")
        
        interviewee = search_result.get("interviewee", "未知受訪者")
        source_file = search_result.get("source_file", 0)
        page_number = search_result.get("page_number", 0)
        score = search_result.get("score", 0)
        
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": "你是一位說中文的大學學長姐，專門回答系統分析課程相關問題，盡量言簡意賅，回答不超過 3-5 句。"},
                {"role": "user", "content": f"學生的問題是：{user_input}\n\n請根據以下資料回答：\n{answer}，\n\n這是與資料相關的提問：{question}"},
            ],
            temperature=0.7,  # 降低隨機性
            top_p=0.9,        # 讓回應更集中
            max_tokens=1000
        )
        print("這裡",answer)
        print(f"Groq API 回應: {response.choices[0].message.content}")
        
        return response.choices[0].message.content, interviewee, score, source_file, page_number, answer
    except Exception as e:
        raise RuntimeError(f"Error from Groq API: {str(e)}")

if __name__ == "__main__":
    get_groq_response("如何追蹤組員進度")