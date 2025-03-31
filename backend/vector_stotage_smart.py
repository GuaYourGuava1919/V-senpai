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

# 強化：過濾異常子題號、加入 page_number 與回答長度、補全 LLM 問題標題

def chunk_interview_text(text, source_file="unknown.pdf"):
    doc = fitz.open(source_file) if os.path.exists(source_file) else None
    page_map = {}
    if doc:
        for i, page in enumerate(doc):
            page_text = page.get_text()
            for line in page_text.splitlines():
                page_map[line.strip()] = i + 1

    interviewee_match = re.search(r"(?:受訪者姓名|訪談學長姓名|受訪者)[^\n：:]*[:：]\s*([\u4e00-\u9fa5、A-Za-z\s]+)", text)
    current_interviewee = interviewee_match.group(1).strip() if interviewee_match else "未知"

    main_pattern = r"(\d+\.\s*.+?)(?=\n\d+\.\s|\Z)"
    main_matches = re.findall(main_pattern, text, re.DOTALL)
    chunks = []

    for main in main_matches:
        lines = main.strip().splitlines()
        main_question = lines[0].strip()
        main_answer = "\n".join(lines[1:]).strip()

        sub_pattern = r"(?:\n)?[（(]?\s*(\d+)[.)）]\s*"
        sub_matches = re.split(sub_pattern, main_answer)

        if len(sub_matches) > 2:
            for i in range(1, len(sub_matches)-1, 2):
                sub_num = sub_matches[i]
                if not sub_num.isdigit() or int(sub_num) > 50:
                    continue
                sub_answer = sub_matches[i+1].strip()
                sub_chunks = re.split(r"\n(?=(?:心得|建議|整理|補充|Q&A|注意事項)[:：])", sub_answer)
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
                            "source_file": source_file,
                            "page_number": page_map.get(section.strip().splitlines()[0], -1),
                            "answer_length": len(section.strip())
                        })
        else:
            sections = re.split(r"\n(?=(?:心得|建議|整理|補充|Q&A|注意事項)[:：])", main_answer)
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
                        "source_file": source_file,
                        "page_number": page_map.get(section.strip().splitlines()[0], -1),
                        "answer_length": len(section.strip())
                    })
    return chunks


def llm_chunk(text, source_file="unknown.pdf"):
    prompt = f"""以下是一段受訪紀錄，請你從中找出所有訪談問題與對應的回答，輸出格式為 JSON 陣列，每筆包含：
- question（問題）
- answer（回答）

若發現段落中只有回答內容，請根據上下文合理推測對應的問題標題並補上。請排除「受訪者姓名」、「班級」、「學號」等不是問題的欄位。

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
    response = co.chat(model="command-r-plus", message=prompt, temperature=0.3, max_tokens=1200)
    try:
        parsed = json.loads(response.text)
        return [
            {
                "chunk_id": str(uuid.uuid4()),
                "interviewee": "未知",
                "question": qa["question"].strip(),
                "answer": qa["answer"].strip(),
                "source_file": source_file,
                "page_number": -1,
                "answer_length": len(qa["answer"].strip())
            }
            for qa in parsed
            if qa.get("question") and qa.get("answer") and is_valid_question(qa["question"])
        ]
    except Exception as e:
        print("❌ LLM 回傳格式錯誤：", str(e))
        return []


# 自動選擇擷取方式並標記方法
def auto_chunk(text, source_file="unknown.pdf"):
    chunks = chunk_interview_text(text, source_file)
    method = "regex"
    if not chunks:
        print(f"⚠️ Regex 擷取失敗，改用 Cohere LLM 萬用抽取：{source_file}")
        chunks = llm_chunk(text, source_file)
        method = "llm" if chunks else "fail"
    return chunks, method

# 處理整個資料夾、產出報告
def process_folder_with_report(folder_path, output_path="all_chunks.json"):
    all_chunks = []
    report = []

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".pdf"):
            full_path = os.path.join(folder_path, filename)
            print(f"\n📄 正在處理：{filename}")
            try:
                text = extract_text_from_pdf(full_path)
                chunks, method = auto_chunk(text, source_file=filename)
                all_chunks.extend(chunks)
                report.append({
                    "filename": filename,
                    "text_length": len(text),
                    "chunk_count": len(chunks),
                    "used_method": method,
                    "sample_question": chunks[0]["question"] if chunks else None
                })
            except Exception as e:
                report.append({
                    "filename": filename,
                    "text_length": 0,
                    "chunk_count": 0,
                    "used_method": f"error: {str(e)}",
                    "sample_question": None
                })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)
    print(f"\n🎉 共 {len(all_chunks)} 筆資料，已儲存至 {output_path}")

    with open("chunk_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print("📊 報告已儲存至 chunk_report.json")

    return all_chunks, report

# 嵌入與上傳函數
def get_embeddings(texts):
    response = co.embed(
        texts=texts,
        model="embed-multilingual-v3.0",
        input_type="search_document",
        embedding_types=["float"]
    )
    return response.embeddings.float

def upsert_chunks(chunks, namespace="interview"):
    from tqdm import tqdm
    existing_ids = set()
    ids_to_check = [c["chunk_id"] for c in chunks]

    BATCH = 100
    for i in range(0, len(ids_to_check), BATCH):
        batch_ids = ids_to_check[i:i+BATCH]
        existing = index.fetch(ids=batch_ids, namespace=namespace)
        existing_ids.update(existing.vectors.keys())

    new_chunks = [c for c in chunks if c["chunk_id"] not in existing_ids]
    if not new_chunks:
        print("⏩ 所有 chunks 都已存在，無需上傳")
        return

    texts = [f"問題：{c['question']}\n回答：{c['answer']}" for c in new_chunks]
    embeddings = get_embeddings(texts)

    vectors = [
        {
            "id": chunk["chunk_id"],
            "values": emb,
            "metadata": {
                "interviewee": chunk["interviewee"],
                "question": chunk["question"],
                "answer": chunk["answer"],
                "source_file": chunk["source_file"],
                "page_number": chunk.get("page_number", -1)
            }
        }
        for chunk, emb in zip(new_chunks, embeddings)
    ]

    index.upsert(vectors=vectors, namespace=namespace)
    print(f"✅ 上傳 {len(vectors)} 筆新向量至 Pinecone（namespace: {namespace}）")

# 主程式入口
if __name__ == "__main__":
    folder_path = "C:\\Users\\Nicole\\Desktop\\vue-project\\files_backup"
    chunks, report = process_folder_with_report(folder_path)

    with open("all_chunks.json", "r", encoding="utf-8") as f:
        chunks = json.load(f)
    print(chunks)

    # 如需上傳向量可取消註解
    # upsert_chunks(chunks, namespace="interview")
