import re
import os
import time

import cohere

import torch
import numpy as np
from transformers import AutoTokenizer, AutoModel
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter

from pinecone import Pinecone, ServerlessSpec

co = cohere.ClientV2()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))


index_name = "systemanalyse" #Pinecone 不允許大寫字母、特殊字符（!、_、空格）。
index_name_2 = "remote-systemanalyse"

# 建立無伺服器索引 (建立一次即可)
# pc.create_index(
#     name=index_name_2,
#     dimension=384, 
#     metric="cosine", 
#     spec=ServerlessSpec(
#         cloud="aws",
#         region="us-east-1"
#     ) 
# )



# 選擇本地嵌入模型
# model_name = "sentence-transformers/multi-qa-MiniLM-L6-cos-v1" #384
# tokenizer = AutoTokenizer.from_pretrained(model_name) 
# model = AutoModel.from_pretrained(model_name) 

# PDF 文件的路徑
file_path = "C:/Users/Nicole/Desktop/vue-project/files/doc1.pdf"

# 載入 PDF 文件
loader = PyPDFLoader(file_path)
document = loader.load()

respondents = []  # 儲存與受訪者相關的內容

for page in document:
    text_content = page.page_content
    print(f"Page content: {text_content}") # 打印頁面內容
    
    respondent_pattern = re.compile(r"受訪者\s*[:：]?\s*(\S+)")  # \S+ 用來匹配非空白字符
    matches = respondent_pattern.findall(text_content) # 使用正則表達式尋找受訪者名稱
    
    for match in matches:
        respondents.append(match)  # 將找到的名字加入 respondents 列表

# 使用文本分割器處理文檔
text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=80)
chunked_documents = text_splitter.split_documents(document)

for i, chunk in enumerate(chunked_documents):
    chunk.metadata['id'] = i+1
    if respondents:  # 確保 respondents 不為空
        chunk.metadata['respondent'] = respondents[i % len(respondents)]
    else:
        chunk.metadata['respondent'] = "未知"  # 如果沒有找到受訪者，設為未知

print(f"Chunked documents: {chunked_documents}")
print(f"Respondents: {respondents}")


# texts = ['第一段文本', '第二段文本', '第三段文本']
texts = [d.page_content for d in chunked_documents]
# tokens = pt['input_ids', 'attention_mask']
# tokens = tokenizer(
#     texts,                 # 輸入文本的列表，例如 ["第一段文本", "第二段文本"]
#     padding=True,          # 啟用填充，確保所有序列長度一致
#     truncation=True,       # 啟用截斷，過長的序列會被截斷到模型的最大長度
#     return_tensors="pt"    # 返回 PyTorch 張量，適用於 PyTorch 模型
# )


response = co.embed(
    texts= texts,
    model="embed-multilingual-light-v3.0",
    input_type="search_document",
    embedding_types=["float"],
)


# # # 生成嵌入
# with torch.no_grad():
#     embeddings = model(**tokens).last_hidden_state.mean(dim=1)
#     print(embeddings[0])  # 打印第一個嵌入向量



vectors = response.embeddings.float  # 這裡的 vectors 可能是 NumPy array 或 PyTorch tensor
vector_list = []  # 用來存放 Pinecone 的向量數據

for document, embedding in zip(chunked_documents, vectors):
    doc_id = document.metadata.get('id')
    text = document.page_content
    respondent = document.metadata.get('respondent', '未知')

    # 確保 embedding 是 NumPy 陣列，並轉換為 float32
    embedding = np.array(embedding, dtype=np.float32)

    if doc_id is not None:
        vector_list.append({  # 使用 vector_list，而不是修改原本的 vectors
            "id": "Vec" + str(doc_id),
            "values": embedding.tolist(),
            "metadata": {
                'text': text,
                'respondent': respondent
            }
        })
    else:
        print(f"Warning: Missing 'id' in the document: {document}")


# for d, e in zip(chunked_documents, embeddings):
#     # 使用 get 方法來避免 KeyError
#     doc_id = d.metadata.get('id')
#     text = d.page_content
#     respondent = d.metadata.get('respondent', '未知')
#     # 確保 'id' 存在
#     if doc_id is not None:
#         vectors.append({
#             "id": "Vec"+str(doc_id),  # 將 ID 轉為字串
#             "values": e.tolist(),  # 將嵌入的張量轉為 Python 列表
#             "metadata": {
#                 'text': text,
#                 'respondent': respondent
#             }
#         })
#     else:
#         print(f"Warning: Missing 'id' in the document: {d}")



# # 打印結果確認
print(vectors)

# # Wait for the index to be ready
while not pc.describe_index(index_name_2).status['ready']:
    time.sleep(1)

index = pc.Index(index_name_2)

index.upsert(
    vectors=vector_list,
    namespace="ns1"
)

# # 使用 describe_index_stats 操作檢查目前的向量數目是否與您倒插的向量數目相符。
print(index.describe_index_stats())
