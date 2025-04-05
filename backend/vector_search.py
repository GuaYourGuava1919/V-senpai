import os
import cohere

import sys
from pinecone import Pinecone
from dotenv import load_dotenv

# 設定標準輸出編碼為 UTF-8
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

# 初始化 Pinecone
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
index_name = "myindex"
index = pc.Index(index_name)


co = cohere.ClientV2()


# 載入 SentenceTransformer 模型（已去掉 torch 和 transformers）
# model = SentenceTransformer("sentence-transformers/multi-qa-MiniLM-L6-cos-v1")

# def vector_search(user_input: str) -> dict:

#     try:
#         # 讓模型直接產生向量
#         query_embedding = model.encode(user_input)
#         #query_embedding = [0.1, 0.2, 0.3, 0.4]  # 假設這是查詢向量

#         # 修正：去掉 `[0]`，直接轉 list
#         results = index.query(
#             namespace="ns1",
#             vector=query_embedding.tolist(),  # 直接轉換成 list
#             top_k=3,
#             include_values=False,
#             include_metadata=True
#         )
#         print(f"Search results: {results}")
        
#         # Extract and combine text
#         texts = [match["metadata"]["text"] for match in results["matches"]]
#         respondent = [match["metadata"]["respondent"] for match in results["matches"]]
#         combined_text = " ".join(texts)
#         print(f"Combined text: {combined_text}")
        
#         return {"combined_text": combined_text, "respondent": respondent}
#     except Exception as e:
#         raise RuntimeError(f"Error during vector search: {str(e)}")

# # 測試範例
# # vector_search("系統分析要注意什麼")

def vector_search_light(user_input: str) -> dict:

    try:
        response = co.embed(
            texts=[user_input],
            model="embed-multilingual-v3.0",
            input_type="search_query",
            embedding_types=["float"],
        )

        # 取得正確的嵌入向量
        vector = response.embeddings.float_[0]

        results = index.query(
            namespace="interview-rag",
            vector=vector,
            top_k=3,
            include_values=False,
            include_metadata=True,
        )

        # print(f"查詢結果: {results}")
        
        
        title = [match["metadata"]["title"] for match in results["matches"]]
        content = [match["metadata"]["content"] for match in results["matches"]]
        interviewee = [match["metadata"]["interviewee"] for match in results["matches"]]
        source = [match["metadata"]["source"] for match in results["matches"]]
        page = [match["metadata"]["page"] for match in results["matches"]]
        score = [match["score"] for match in results["matches"]]
        
        #將問題答案組合成一個字串
        title = " ".join(title)
        content = " ".join(content)
        
        #去除重複的interviewee
        # interviewee = list(set(interviewee))
        
        #去除重複的source_file
        # source = list(set(source))
        
        #去除重複的page_number
        # page = list(set(page))
        
        #平均分數
        avg_score = sum(score) / len(score) if score else 0
        
        # print(f"查詢結果: {results}")
        # print(f"問題: {user_input}")
        # print(f"標題: {title}")
        # print(f"內容: {content}")
        # print(f"受訪者: {interviewee}")
        # print(f"來源: {source}")
        # print(f"頁碼: {page}")
        # print(f"分數: {avg_score}")
        
        # 返回查詢結果
        return {
            "question": user_input,
            "answer": content,
            "interviewee": interviewee,
            "source_file": source,
            "page_number": page,
            "score": avg_score,
        }

    except Exception as e:
        raise RuntimeError(f"Error during vector search: {str(e)}")


if __name__ == "__main__":
    # 測試範例
    vector_search_light("如何追蹤組員進度")
