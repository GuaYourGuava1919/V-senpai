import re
import time
import torch
from pinecone import Pinecone, ServerlessSpec
from transformers import AutoTokenizer, AutoModel
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter


pc = Pinecone(api_key="pcsk_VPkZN_FYg8jEj3q9F8MNzqQzBXXGhrtzRPzhY4C8A4W4mPBHCrX8eUQ8QMPTD3FZCtGFe")

# 設定索引來儲存資料。

# 建立無伺服器索引 (建立一次即可)
index_name = "quicktest"

# pc.create_index(
#     name=index_name,
#     dimension=384, # Replace with your model dimensions
#     metric="cosine", # Replace with your model metric
#     spec=ServerlessSpec(
#         cloud="aws",
#         region="us-east-1"
#     ) 
# )


# 選擇嵌入模型
model_name = "sentence-transformers/multi-qa-MiniLM-L6-cos-v1" #384
tokenizer = AutoTokenizer.from_pretrained(model_name) 
model = AutoModel.from_pretrained(model_name) 

# PDF 文件的路徑
file_path = "C:/Users/Nicole/Desktop/vue-project/files/doc1.pdf"

# 載入 PDF 文件
loader = PyPDFLoader(file_path)
document = loader.load()

respondents = []  # 儲存與受訪者相關的內容

# 假設你已經擁有 document 變數，這是每頁的內容
for page in document:
    text_content = page.page_content
    print(f"Page content: {text_content}")  # 打印每頁內容進行調試
    
    respondent_pattern = re.compile(r"受訪者\s*[:：]?\s*(\S+)")  # \S+ 用來匹配非空白字符
    
    matches = respondent_pattern.findall(text_content)
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


texts = [d.page_content for d in chunked_documents]
tokens = tokenizer(
    texts,                 # 輸入文本的列表，例如 ["第一段文本", "第二段文本"]
    padding=True,          # 啟用填充，確保所有序列長度一致
    truncation=True,       # 啟用截斷，過長的序列會被截斷到模型的最大長度
    return_tensors="pt"    # 返回 PyTorch 張量，適用於 PyTorch 模型
)

# # 生成嵌入
with torch.no_grad():
    embeddings = model(**tokens).last_hidden_state.mean(dim=1)
    print(embeddings[0])  # 打印第一個嵌入向量


# # 將產生的向量內嵌倒插到索引中新的 ns2 命名空間中。
vectors = []
for d, e in zip(chunked_documents, embeddings):
    # 使用 get 方法來避免 KeyError
    doc_id = d.metadata.get('id')
    text = d.page_content
    respondent = d.metadata.get('respondent', '未知')
    # 確保 'id' 存在
    if doc_id is not None:
        vectors.append({
            "id": "Vec"+str(doc_id),  # 將 ID 轉為字串
            "values": e.tolist(),  # 將嵌入的張量轉為 Python 列表
            "metadata": {
                'text': text,
                'respondent': respondent
            }
        })
    else:
        print(f"Warning: Missing 'id' in the document: {d}")



# # 打印結果確認
print(vectors)

# # Wait for the index to be ready
while not pc.describe_index(index_name).status['ready']:
    time.sleep(1)

index = pc.Index(index_name)

index.upsert(
    vectors=vectors,
    namespace="ns1"
)

# # 使用 describe_index_stats 操作檢查目前的向量數目是否與您倒插的向量數目相符。
print(index.describe_index_stats())

# 在資料中搜尋與查詢向量語意相似的項目。
# query = "Tell me about the tech company known as Apple."

# embedding = pc.inference.embed(
#     model="multilingual-e5-large",
#     inputs=[query],
#     parameters={
#         "input_type": "query"
#     }
# )
# 查詢 ns1 命名空間中與查詢向量最相似的三個向量，也就是代表與問題最相關答案的向量：
# results = index.query(
#     namespace="ns1",
#     vector=embedding[0].values,
#     top_k=3,
#     include_values=False,
#     include_metadata=True
# )

# print(results)