import re
import os

import cohere
from pinecone import Pinecone, ServerlessSpec

import numpy as np
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader

# **加載環境變數**
load_dotenv()
co = cohere.Client(os.getenv("CO_API_KEY"))
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

index_name= "chunking-test-dotproduct"

# **檢查索引是否存在**
# if index_name_3 not in pc.list_indexes():
#     print(f"索引 {index_name_3} 不存在，請先建立索引！")
#     exit(1)

# 建立無伺服器索引 (建立一次即可)
# pc.create_index(
#     name=index_name,
#     dimension=384, 
#     metric="dotproduct", 
#     spec=ServerlessSpec(
#         cloud="aws",
#         region="us-east-1"
#     ) 
# )

# **讀取 PDF**
file_path = "C:/Users/Nicole/Desktop/vue-project/files/doc1.pdf"
loader = PyPDFLoader(file_path)
document = loader.load()

full_text = "\n".join([page.page_content for page in document])
print(full_text)

# **正則表達式**
question_pattern = r"(?:\d+[\.\s]*)?(?:[（\(]\d+[）\)]\s*)?([\u4e00-\u9fa5\s,]{2,100}？(?:\s*[\u4e00-\u9fa5\s,]{2,100}？)*)"

respondent_pattern = r"(?:受訪者姓名|學長姐訪談受訪者姓名|受訪者)\s*[:：]?\s*([\u4e00-\u9fa5、，, ]+)"


# **分割文本**
raw_chunks = re.split(f"({question_pattern}|{respondent_pattern})", full_text)
raw_chunks = [chunk.strip() for chunk in raw_chunks if isinstance(chunk, str) and chunk.strip()]



chunked_documents = []
current_question = None
current_respondent = "未知"

for chunk in raw_chunks:
    # **如果是受訪者，更新 `current_respondent`**
    respondent_match = re.search(respondent_pattern, chunk)
    if respondent_match:
        current_respondent = respondent_match.group(1).strip()
        current_respondent = re.sub(r"[（）\(\)【】\[\]]", "", current_respondent)
        current_respondent = current_respondent.replace("、", ", ")  
        print(f"✅ 找到受訪者: {current_respondent}")  # Debug
        continue  

    # **如果是問題，更新 `current_question`**
    if re.match(question_pattern, chunk):
        current_question = chunk
    else:
        if current_question:
            formatted_response = f"{current_respondent} 說：{chunk}"
            chunked_documents.append({
                "question": current_question,
                "response": formatted_response,
                "respondent": current_respondent
            })
            print(f"✅ 儲存問答組合: {current_question} -> 受訪者: {current_respondent}")  # Debug
            current_question = None  


if not chunked_documents:
    print("❌ chunked_documents 是空的，請檢查正則表達式是否正確匹配問題！")
else:
    print("=== 最終切割結果 ===")
    for doc in chunked_documents[:5]:  # 顯示前 5 個
        print(f"問題: {doc['question']}")
        print(f"回應: {doc['response']}")
        print(f"受訪者: {doc['respondent']}")
        print("-" * 50)


# **解析問題 + 回應**
# chunked_documents = []
# current_question = None
# current_respondent = ""

# for chunk in interview_chunks:
#     if re.match(question_pattern, chunk):  
#         current_question = chunk
#         current_respondent = "未知"
#     else:
#         if current_question:
#             respondent_match = re.search(respondent_pattern, chunk)
#             if respondent_match:
#                 current_respondent = respondent_match.group(1)  

#             chunked_documents.append({
#                 "question": current_question,
#                 "response": chunk,
#                 "respondent": current_respondent
#             })
#             current_question = None

# **嵌入向量**
# vector_list = []
# for idx, chunk in enumerate(chunked_documents):
#     text_to_embed = f"問題: {chunk['question']}\n回應: {chunk['response']}"
#     response = co.embed(texts=[text_to_embed], model="embed-multilingual-light-v3.0", input_type="search_document", embedding_types=["float"])

#     if hasattr(response.embeddings, "float"):
#         vectors = np.array(response.embeddings.float, dtype=np.float32)
#     elif isinstance(response.embeddings, list):
#         vectors = np.array(response.embeddings, dtype=np.float32)
#     else:
#         raise TypeError(f"Unexpected response.embeddings type: {type(response.embeddings)}")


#     vector_list.append({
#     "id": f"Vec{idx}",
#     "values": vectors.flatten().tolist(),  # ✅ 確保是 List[float]
#     "metadata": {
#         "question": chunk["question"],
#         "response": chunk["response"],
#         "respondent": chunk["respondent"]
#         }
#     })
    


# **上傳至 Pinecone**
# index = pc.Index(index_name)
# index.upsert(vectors=vector_list, namespace="ns1")

# print(f"成功上傳 {len(vector_list)} 條向量到 Pinecone！")

