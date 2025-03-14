import io
import re
import os
import base64
import cohere
from dotenv import load_dotenv
import google.generativeai as genai
from pdf2image import convert_from_path
from langchain.document_loaders import PyPDFLoader
from pinecone import Pinecone, ServerlessSpec
import time

load_dotenv()

# ====== 設定 Cohere 與 Gemini ======
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

co = cohere.Client(COHERE_API_KEY)
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel(model_name="gemini-2.0-flash")

# ====== Pinecone 設定 ======
from pinecone import Pinecone, ServerlessSpec
pc = cohere.Client(COHERE_API_KEY)

load_dotenv()

def process_page(image_b64):
    payload = [
        {"inline_data": {"data": image_b64, "mime_type": "image/png"}},
        {"text": "（你的原prompt內容，或自定義prompt）"}
    ]

    response = model.generate_content(payload)
    return response.text

def extract_chunks(text_out, respondent):
    chunk_pattern = re.compile(
        r"<chunk>\s*<chunk_title>(.*?)<\/chunk_title>\s*<chunk_text>(.*?)<\/chunk_text>\s*</chunk>",
        re.DOTALL
    )

    chunks = []
    for match in chunk_pattern.finditer(text_out):
        title = match.group(1).strip()
        chunk_text = match.group(2).strip()
        if not title:
            title = "Undefined"
        return {"chunk_title": title, "chunk_text": chunk_text, "respondent": respondent}

def get_respondent(full_text):
    respondent_pattern = r"(?:受訪者姓名|學長姐訪談受訪者姓名)[：:]\s*([\u4e00-\u9fa5、，, ]+)"
    match = re.search(respondent_pattern, full_text)
    if match:
        respondent = match.group(1).strip().split()[0]
        respondent = re.sub(r"[（）\(\)【】\[\]]", "", respondent)
    else:
        respondent = "未知"
    return respondent

def process_and_upload(pdf_path, index_name, namespace):
    from langchain.document_loaders import PyPDFLoader
    from pinecone import Pinecone, ServerlessSpec
    from pdf2image import convert_from_path
    
    pc = Pinecone(api_key=PINECONE_API_KEY)
    pc_index = pc.Index(index_name)

    loader = PyPDFLoader(pdf_path)
    document = loader.load()
    full_text = "\n\n".join(page.page_content for page in document)
    respondent = get_respondent(full_text)

    pages = convert_pdf_to_images(pdf_path)

    vector_list = []

    for page_no, page in enumerate(pages, start=1):
        buffer = io.BytesIO()
        page.save(buffer, format="PNG")
        image_data = buffer.getvalue()
        image_b64 = base64.b64encode(image_data).decode("utf-8")

        text_out = process_page(page_no, image_data)
        chunk_data = extract_chunks(text_out=text_out, respondent=respondent)

        embed_text = f"{chunk_data['chunk_title']}\n{chunk_data['chunk_text']}"
        embedding_resp = co.embed(
            texts=[embed_text],
            model="embed-multilingual-v3.0",
            input_type="search_document",
            embedding_types=["float"]
        )

        embedding = embedding_resp.embeddings[0]

        vector_list.append({
            "id": f"{os.path.basename(pdf_path)}-{page_no}",
            "values": embedding,
            "metadata": {
                "chunk_title": chunk_data["chunk_title"],
                "chunk_text": chunk_data["chunk_text"],
                "respondent": respondent,
                "source_file": os.path.basename(pdf_path),
                "page_no": page_no
            })

    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(index_name)
    index.upsert(vectors=vector_list, namespace=namespace)
    print(f"Uploaded chunks from file: {pdf_path}")

def convert_pdf_to_images(pdf_file):
    from pdf2image import convert_from_path
    pages = convert_from_path(pdf_file)
    return pages

def run_folder(folder_path, index_name, namespace):
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".pdf"):
            file_path = os.path.join(folder, filename)
            print(f"Processing file: {filename}")
            process_and_upload(file_path, index_name, namespace)
            print(f"Completed processing: {filename}")

if __name__ == "__main__":
    folder = "C:/Users/Nicole/Desktop/vue-project/files"
    index_name = "chunking-gemini-dotproduct-2"
    namespace = "ns1"
    process_folder(folder, index_name, namespace)
