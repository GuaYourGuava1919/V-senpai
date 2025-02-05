import sys
import torch
from pinecone import Pinecone, ServerlessSpec
from transformers import AutoTokenizer, AutoModel

sys.stdout.reconfigure(encoding='utf-8')

pc = Pinecone(api_key="pcsk_VPkZN_FYg8jEj3q9F8MNzqQzBXXGhrtzRPzhY4C8A4W4mPBHCrX8eUQ8QMPTD3FZCtGFe")
index_name = "quicktest"
index = pc.Index(index_name)

model_name = "sentence-transformers/multi-qa-MiniLM-L6-cos-v1" #384
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name) 



def vector_search(user_input: str) -> dict:
    """
    查詢 Pinecone 向量索引並返回相關文本結果。

    Args:
        user_input (str): 使用者查詢輸入。

    Returns:
        dict: 包含組合文本 ('combined_text') 和原始查詢結果 ('results')。
    """
    try:
        # Tokenize user input
        query_tokens = tokenizer(
            user_input, padding=True, truncation=True, return_tensors="pt"
        )
        # Generate embedding
        with torch.no_grad():
            query_embedding = model(**query_tokens).last_hidden_state.mean(dim=1)

        # Query Pinecone
        results = index.query(
            namespace="ns1",
            vector=query_embedding[0].tolist(),
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
        # Raise a more informative error
        raise RuntimeError(f"Error during vector search: {str(e)}")



# vector_search("系統分析要注意什麼")