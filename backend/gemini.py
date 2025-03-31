import io
import re
import os
import base64
import cohere
from dotenv import load_dotenv
import google.generativeai as genai
from pdf2image import convert_from_path  # 需要先安裝 poppler 以支援 PDF 轉圖片
from pinecone import Pinecone, ServerlessSpec
from langchain_community.document_loaders import PyPDFLoader

load_dotenv()

# ====== 0. 設定 Cohere Client ======
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
co = cohere.Client(COHERE_API_KEY)

# ====== PDF 轉圖片部分 (範例) ======
pdf_file = "C:/Users/Nicole/Desktop/vue-project/files/doc15.pdf"
poppler_path = r"C:\\Users\\Nicole\\Downloads\\Release-24.08.0-0\\poppler-24.08.0\\Library\\bin"
pages = convert_from_path(pdf_file, poppler_path=poppler_path)
print(f"Converted {len(pages)} PDF pages to images.")

images_b64 = {}
for i, page in enumerate(pages, start=1):
    buffer = io.BytesIO()
    page.save(buffer, format="PNG")
    image_data = buffer.getvalue()
    b64_str = base64.b64encode(image_data).decode("utf-8")
    images_b64[i] = b64_str

print("第一頁的 Base64 編碼內容：", images_b64[1][:100], "...")

# ====== Google Generative AI 設定 ======
GOOGLE_API_KEY = "AIzaSyBtfyLJV7VZEMW7kMdkjAsM0Kt0MzEIRpI"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel(model_name="gemini-2.0-flash")
print("Gemini model loaded:", model)

# ====== Prompt 範例 ======
# 也可要求模型務必以下列格式輸出:
# <chunk>
#   <chunk_title>可能有，可能沒有</chunk_title>
#   <chunk_text>必需有</chunk_text>
# </chunk>
CHUNKING_PROMPT = """\
OCR the following page into Markdown. Tables should be formatted as HTML.
Do not surround your output with triple backticks.
Chunk the document into sections of roughly 250 - 1000 words.

Give every chunk_text a summerized title, if you can't find a title, use "".
use traditional chinese language.

For each chunk, output the following format:
<chunk>
<chunk_title>... (optional) ...</chunk_title>
<chunk_text>... (required) ...</chunk_text>
</chunk>

Preserve as much content as possible, including headings, tables, etc.
"""

def process_page(page_num, image_b64):
    """呼叫 Google Generative AI 將圖片進行 OCR，並解析 <title>、可選的 <chunk_title>、以及 <chunk_text>。"""
    payload = [
        {
            "inline_data": {"data": image_b64, "mime_type": "image/png"}
        },
        {
            "text": CHUNKING_PROMPT
        }
    ]
    try:
        print(f"processing page {page_num}")
        resp = model.generate_content(payload)
        text_out = resp.text
    except Exception as e:
        print(f"Error processing page {page_num}: {e}")
        return []

    # 設計一個可同時容忍 <chunk_title> 沒有的情況的正則
    # 使用 (?: ... )? 表示該區塊可存在也可不存在
    # (?P<title>) 與 (?P<text>) 透過命名群組, 方便後面取用
    chunk_pattern = re.compile(
        r"<chunk>\s*"
        r"(?:<chunk_title>(?P<title>.*?)</chunk_title>\s*)?"
        r"<chunk_text>(?P<text>.*?)</chunk_text>\s*"
        r"</chunk>",
        re.DOTALL
    )
    chunk_matches = chunk_pattern.finditer(text_out)

    results = []
    for idx, match in enumerate(chunk_matches):
        chunk_title = match.group("title") if match.group("title") else "Undefined"
        chunk_text = match.group("text").strip()

        # 如果確定要 "只要有 chunk text 就記錄"
        # -> 檢查 chunk_text 是否為空
        if chunk_text:
            results.append({
                "id": f"page_{page_num}_chunk_{idx}",
                "chunk_title": chunk_title.strip(),
                "chunk_text": chunk_text
            })

    # 如果連一個 chunk 也沒有，就做 fallback
    if not results:
        print("Warning: No <chunk> pattern found; using fallback splitting...")
        splitted = text_out.strip().split("\n\n")
        for idx, chunk_txt in enumerate(splitted):
            if chunk_txt.strip():  # 只要非空就記錄
                results.append({
                    "id": f"page_{page_num}_chunk_{idx}",
                    "chunk_title": "Undefined",
                    "chunk_text": chunk_txt.strip()
                })

    return results


loader = PyPDFLoader(pdf_file)
document = loader.load()

full_text = "\n\n".join([page.page_content for page in document])

current_respondent = "未知"
respondent_pattern = r"(?:受訪者姓名|學長姐訪談受訪者姓名|受訪者)\s*[:：]?\s*(.+)"
respondent_match = re.search(respondent_pattern, full_text)

if respondent_match:
    current_respondent = respondent_match.group(1).strip()
    
    # 移除括號內容
    current_respondent = re.sub(r"[（(【\[].*?[）)】\]]", "", current_respondent)

    # 移除系級資訊 (例如: 資管三甲)
    current_respondent = re.sub(r"[\u4e00-\u9fa5]{2,6}[一二三四五六七八九十甲乙丙丁戊己庚辛壬癸]+", "", current_respondent)

    # 移除稱謂（學姐、學長、同學、老師、教授）
    current_respondent = re.sub(r"(學姐|學長|同學|老師|教授)", "", current_respondent)

    current_respondent = current_respondent.strip()

    # 處理是否有頓號
    if re.search(r"[、，,]", current_respondent):
        names = [name.strip() for name in re.split(r"[、，,]+", current_respondent)]
        valid_names = [name for name in names if re.fullmatch(r"[\u4e00-\u9fa5]{2,4}", name)]
        document_respondents = ", ".join(valid_names) if valid_names else "未知"
    else:
        # 空格情況只取第一個
        first_name = current_respondent.split()[0]
        if re.fullmatch(r"[\u4e00-\u9fa5]{2,4}", first_name):
            document_respondents = first_name
        else:
            document_respondents = "未知"

    print(f"✅ 找到受訪者: {document_respondents}")  # Debug
else:
    document_respondents = "未知"
    print("❌ 找不到受訪者")  # Debug


# 處理整份 PDF
all_chunks = []
for i, b64_str in images_b64.items():
    page_chunks = process_page(i, b64_str)
    for page_chunk in page_chunks:
        page_chunk["document_respondents"] = document_respondents
    all_chunks.extend(page_chunks)

print(f"Total extracted chunks: {len(all_chunks)}")

# ====== 5. Embedding with Cohere ======
# 這裡使用 co.embed(texts=[...]) 來拿到向量；根據 chunk 數量大小，我們可一次或分批 Embedding
text_to_embeded_list = [f"{chunk_data["chunk_title"]}\n{chunk_data["chunk_text"]}" for chunk_data in all_chunks]
# text_to_embeded_list = [all_chunks[0]["chunk_text"],all_chunks[1]["chunk_text"],all_chunks[2]["chunk_text"]]

# 呼叫 Cohere 的多語言輕量版本 embed-multilingual-light-v3.0
# input_type="search_document" 表示此文本將用於被檢索的文件向量
# embedding_types=["float"] 代表我們要拿到 float 向量
response = co.embed(
    texts=text_to_embeded_list,
    model="embed-multilingual-v3.0",
    input_type="search_document",
    embedding_types=["float"]
)
# response.embeddings 會回傳一個 list，每個元素是一個向量
print(f"Embedding response: {response.meta}...")


for i in range(len(all_chunks)):
    chunk = all_chunks[i]
    chunk["embedding"] = response.embeddings.float[i]

# ====== 6. 儲存最終結果 ======
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name= "chunking-gemini-dotproduct-2"
# 建立無伺服器索引 (建立一次即可)
# pc.create_index(
#     name=index_name,
#     dimension=1024, 
#     metric="dotproduct", 
#     spec=ServerlessSpec(
#         cloud="aws",
#         region="us-east-1"
#     ) 
# )

vector_list = []
for idx,chunk_data in enumerate(all_chunks):
    print(f"\nID: {chunk_data['id']}")
    print(f"Title: {chunk_data['chunk_title']}")
    print(f"Text: {chunk_data['chunk_text'][:50]}...")  # 只顯示前 50 字
    print(f"Embedding (部分): {chunk_data['embedding'][:8]}...")  # 只顯示向量前 8 維
    vector_list.append({
        "id": chunk_data["id"],
        "values": chunk_data['embedding'],  # ✅ 確保是 List[float]
        "metadata": {
            "text": chunk_data['chunk_text'],
            "title": chunk_data['chunk_title'],
            "respondents": chunk_data['document_respondents']
        }
    })
    

# **上傳至 Pinecone**
index = pc.Index(index_name)
index.upsert(vectors=vector_list, namespace="ns1")