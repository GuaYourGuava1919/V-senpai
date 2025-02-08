import os
import sys
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

# 設定標準輸出編碼為 UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# 初始化 Pinecone
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
index_name = "systemanalyse"
index = pc.Index(index_name)

# 載入 SentenceTransformer 模型（已去掉 torch 和 transformers）
model = SentenceTransformer("sentence-transformers/multi-qa-MiniLM-L6-cos-v1")

def vector_search(user_input: str) -> dict:
    """
    查詢 Pinecone 向量索引並返回相關文本結果。

    Args:
        user_input (str): 使用者查詢輸入。

    Returns:
        dict: 包含組合文本 ('combined_text') 和原始查詢結果 ('results')。
    """
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
