import os
from groq import Groq
from backend.vector_search import vector_search

def get_groq_response(user_input: str) -> str:
    try:
        # 初始化 Groq 客户端
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

        # 执行向量搜索并获取结果
        search_result = vector_search(user_input)
        
        # 提取搜索结果中的 'combined_text'
        combined_text = search_result.get("combined_text", "我們無法找到相關的資料，請詳細說明或重試。")
        # 提取搜索结果中的 'respondent'
        respondent = search_result.get("respondent", "未知")
        
        # 向 Groq 提交请求，并传递上下文
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # 替换为你要使用的 Groq 模型
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
        
        # 返回 Groq 回应内容
        return response.choices[0].message.content, respondent
    except Exception as e:
        # 错误处理
        raise RuntimeError(f"Error from Groq API: {str(e)}")
