import os
import re
import uuid
import json
import fitz  # PyMuPDF
import cohere
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

# 加載環境變數
load_dotenv()

# 初始化 Cohere 客戶端
co = cohere.Client("nyJzgBpibkpcykwBIfvUij8bbyITEVcBJVqc2zvN")

# 初始化 Pinecone 實例
pc = Pinecone(api_key="pcsk_574hwv_HimevaC5VKUfXogLB2e9g1Ufe8fEyxyWjxoiMfxvvGEux6u1A1ubrrssJkuz5mo")

# 檢查 index 是否存在
if "myindex" not in pc.list_indexes().names():
    pc.create_index(
        name="myindex",
        dimension=1024,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

index = pc.Index("myindex")

# 定義 PDF 文字提取函數
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# 定義非問題前綴
NON_QUESTION_PREFIXES = ["受訪者", "班級", "姓名", "學號", "學長姐", "訪談者", "主題", "none", "n/a"]

# 定義問題驗證函數
def is_valid_question(q):
    q = q.strip().lower()
    if not q or len(q) < 3:
        return False
    if any(prefix in q for prefix in NON_QUESTION_PREFIXES):
        return False
    if re.match(r"^[a-zA-Z0-9\s\.:：、，。()（）]+$", q) and len(q) < 10:
        return False
    return True

# 定義分層擷取函數
def chunk_interview_text(text, source_file="unknown.pdf"):
    interviewee_match = re.search(r"(?:受訪者姓名|訪談學長姓名|受訪者)[^\n：:]*[:：]\s*([\u4e00-\u9fa5、A-Za-z\s]+)", text)
    current_interviewee = interviewee_match.group(1).strip() if interviewee_match else "未知"

    # 擷取主題大題：例如 1. 問題？
    main_pattern = r"(\d+\.\s*.+?)(?=\n\d+\.\s|\Z)"
    main_matches = re.findall(main_pattern, text, re.DOTALL)

    chunks = []

    for main in main_matches:
        lines = main.strip().splitlines()
        main_question = lines[0].strip()
        main_answer = "\n".join(lines[1:]).strip()

        # 改善子題切分：支援 (1) 1. 1）等格式
        sub_pattern = r"(?:\n)?[（(]?\s*(\d+)[.)）]\s*"
        sub_matches = re.split(sub_pattern, main_answer)

        if len(sub_matches) > 2:
            for i in range(1, len(sub_matches)-1, 2):
                sub_num = sub_matches[i]
                sub_answer = sub_matches[i+1].strip()

                # 特別處理延伸心得切分
                sub_chunks = re.split(r"\n(?=(?:心得|建議|整理|補充|Q&A|注意事項)[：:])", sub_answer)
                for j, section in enumerate(sub_chunks):
                    q_label = f"{main_question} - 子題 {sub_num}"
                    if len(sub_chunks) > 1:
                        q_label += f"（段落 {j+1}）"
                    if is_valid_question(q_label) and section:
                        chunks.append({
                            "chunk_id": str(uuid.uuid4()),
                            "interviewee": current_interviewee,
                            "question": q_label,
                            "answer": section.strip(),
                            "source_file": source_file
                        })
        else:
            # 無子題時也處理心得延伸段落
            sections = re.split(r"\n(?=(?:心得|建議|整理|補充|Q&A|注意事項)[：:])", main_answer)
            for j, section in enumerate(sections):
                label = main_question
                if len(sections) > 1:
                    label += f"（段落 {j+1}）"
                if is_valid_question(label) and section:
                    chunks.append({
                        "chunk_id": str(uuid.uuid4()),
                        "interviewee": current_interviewee,
                        "question": label,
                        "answer": section.strip(),
                        "source_file": source_file
                    })

    print(f"✅ 分層擷取 {len(chunks)} 筆 chunk（受訪者：{current_interviewee}，檔案：{source_file}）")
    if chunks:
        print(f"範例問題：{chunks[0]['question']}")
        print(f"範例回答：{chunks[0]['answer'][:60]}...")
    print("========================================")
    return chunks


# 定義 LLM 擷取函數
def llm_chunk(text, source_file="unknown.pdf"):
    prompt = f"""以下是一段受訪紀錄，請你從中找出所有訪談問題與對應的回答，輸出格式為 JSON 陣列，每筆包含：
- question（問題）
- answer（回答）

請排除「受訪者姓名」、「班級」、「學號」等不是問題的欄位。

文字如下：
{text}

請回傳 JSON 陣列：
[
  {{
    "question": "...",
    "answer": "..."
  }},
  ...
]"""

    response = co.chat(
        model="command-r-plus",
        message=prompt,
        temperature=0.3,
        max_tokens=1200
    )

    try:
        parsed = json.loads(response.text)
        chunks = []
        for qa in parsed:
            if qa.get("question") and qa.get("answer") and is_valid_question(qa["question"]):
                chunks.append({
                    "chunk_id": str(uuid.uuid4()),
                    "interviewee": "未知",
                    "question": qa["question"].strip(),
                    "answer": qa["answer"].strip(),
                    "source_file": source_file
                })
        return chunks
    except Exception as e:
        print("❌ LLM 回傳格式錯誤：", str(e))
        return []

# 定義自動選擇擷取方法
def auto_chunk(text, source_file="unknown.pdf"):
    chunks = chunk_interview_text(text, source_file)
    if chunks:
        return chunks
    else:
        print(f"⚠️ Regex 失敗，改用 Cohere LLM 萬用抽取中...")
        return llm_chunk(text, source_file)

# 定義處理資料夾的函數
def process_folder(folder_path, output_path="all_chunks.json"):
    all_chunks = []
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".pdf"):
            full_path = os.path.join(folder_path, filename)
            print(f"\n📄 正在處理：{filename}")
            try:
                text = extract_text_from_pdf(full_path)
                chunks = auto_chunk(text, source_file=filename)
                if chunks:
                    all_chunks.extend(chunks)
                    print(f"✅ 完成：{filename}（{len(chunks)} 筆 chunk）")
                else:
                    print(f"⚠️ 無 chunk：{filename}")
            except Exception as e:
                print(f"❌ 錯誤處理 {filename}：{str(e)}")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)
    print(f"\n🎉 共 {len(all_chunks)} 筆資料，已儲存至 {output_path}")

# 定義嵌入與上傳函數
def get_embeddings(texts):
    response = co.embed(
        texts=texts,
        model="embed-multilingual-v3.0",
        input_type="search_document",
        embedding_types=["float"]
    )
    return response.embeddings.float

# 定義上傳 chunks 函數
def upsert_chunks(chunks, namespace="interview"):
    from tqdm import tqdm

    existing_ids = set()
    ids_to_check = [c["chunk_id"] for c in chunks]

    # 批次查詢已存在向量
    BATCH = 100
    for i in range(0, len(ids_to_check), BATCH):
        batch_ids = ids_to_check[i:i+BATCH]
        existing = index.fetch(ids=batch_ids, namespace=namespace)
        existing_ids.update(existing.vectors.keys())

    # 過濾已存在的 chunks
    new_chunks = [c for c in chunks if c["chunk_id"] not in existing_ids]
    if not new_chunks:
        print("⏩ 所有 chunks 都已存在，無需上傳")
        return

    # 進行嵌入與上傳
    texts = [f"問題：{c['question']}\n回答：{c['answer']}" for c in new_chunks]
    embeddings = get_embeddings(texts)

    vectors = []
    for chunk, emb in zip(new_chunks, embeddings):
        vectors.append({
            "id": chunk["chunk_id"],
            "values": emb,
            "metadata": {
                "interviewee": chunk["interviewee"],
                "question": chunk["question"],
                "answer": chunk["answer"],
                "source_file": chunk["source_file"],
                "page_number": chunk.get("page_number", -1)
            }
        })

    index.upsert(vectors=vectors, namespace=namespace)
    print(f"✅ 上傳 {len(vectors)} 筆新向量至 Pinecone（namespace: {namespace}）")


if __name__ == "__main__":
    folder_path = "C:\\Users\\Nicole\\Desktop\\vue-project\\files_backup"
    process_folder(folder_path)

    with open("all_chunks.json", "r", encoding="utf-8") as f:
        chunks = json.load(f)
        print(chunks)

    # upsert_chunks(chunks, namespace="interview")

