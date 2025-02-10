import os
import cohere

import sys
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

# 設定標準輸出編碼為 UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# 初始化 Pinecone
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
index_name = "remote-systemanalyse"
index = pc.Index(index_name)


co = cohere.ClientV2()

# 載入 SentenceTransformer 模型（已去掉 torch 和 transformers）
model = SentenceTransformer("sentence-transformers/multi-qa-MiniLM-L6-cos-v1")

def vector_search(user_input: str) -> dict:

    try:
        # 讓模型直接產生向量
        query_embedding = model.encode(user_input)
        #query_embedding = [0.1, 0.2, 0.3, 0.4]  # 假設這是查詢向量

        # 修正：去掉 `[0]`，直接轉 list
        results = index.query(
            namespace="ns1",
            vector=query_embedding.tolist(),  # 直接轉換成 list
            top_k=3,
            include_values=False,
            include_metadata=True
        )
        print(f"Search results: {results}")
        
        # Extract and combine text
        texts = [match["metadata"]["text"] for match in results["matches"]]
        respondent = [match["metadata"]["respondent"] for match in results["matches"]]
        combined_text = " ".join(texts)
        print(f"Combined text: {combined_text}")
        
        return {"combined_text": combined_text, "respondent": respondent}
    except Exception as e:
        raise RuntimeError(f"Error during vector search: {str(e)}")

# 測試範例
# vector_search("系統分析要注意什麼")

def vector_search_light(user_input: str) -> dict:

    try:
        response = co.embed(
            texts=[user_input],
            model="embed-multilingual-light-v3.0",
            input_type="search_query",
            embedding_types=["float"],
        )
        print(f"輸入文字：{response}")
        
        # 取得正確的嵌入向量
        vector = response.embeddings.float_[0]  # 正確獲取嵌入向量
        print(f"Vector: {vector}")
        
        results = index.query(
                namespace="ns1",
                vector=vector,
                top_k=3,
                include_values=False,
                include_metadata=True
            )
        
        print(f"查詢結果: {results}")
        
        texts = [match["metadata"]["text"] for match in results["matches"]]
        respondent = [match["metadata"]["respondent"] for match in results["matches"]]
        combined_text = " ".join(texts)
        print(f"Combined text: {combined_text}")
        
        return {"combined_text": combined_text, "respondent": respondent}

    except Exception as e:
        raise RuntimeError(f"Error during vector search: {str(e)}")

# vector_search_light("系統分析要注意什麼")
