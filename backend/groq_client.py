import os
from groq import Groq
# from backend.vector_search import vector_search
from backend.vector_search_light import vector_search_light


def get_groq_response(user_input: str) -> str:
    try:
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        
        search_result = vector_search_light(user_input)
        
        combined_text = search_result.get("combined_text", "我們無法找到相關的資料，請詳細說明或重試。")
        respondent = search_result.get("respondent", "未知")
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
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
