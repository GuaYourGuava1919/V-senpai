import os
import cohere
from pinecone import Pinecone


# 初始化 Pinecone
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
index_name = "quicktest"
index = pc.Index(index_name)

co = cohere.ClientV2()

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

vector_search_light("系統分析要注意什麼")