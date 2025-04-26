from langchain_community.vectorstores import FAISS  
from langchain_huggingface import HuggingFaceEmbeddings
from huggingface_hub import InferenceClient
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from PyPDF2 import PdfReader
from dotenv import load_dotenv

HUGGINGFACE_API_KEY= os.getenv("HUGGINGFACE_API_KEY")

client = InferenceClient(
    model="mistralai/Mixtral-8x7B-Instruct-v0.1",
    token=HUGGINGFACE_API_KEY
)

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


VECTOR_PATH = "vectorstore/faiss_index"

def ask_huggingface(prompt: str):
    response = client.text_generation(
        prompt=prompt,
        max_new_tokens=1000,
        temperature=0.1,
    )
    return response

def ask_question(question: str, history: list[dict]):
    if not os.path.exists(VECTOR_PATH):
        return "❌ Không tìm thấy FAISS index. Vui lòng upload tài liệu trước."

    vector_store = FAISS.load_local(VECTOR_PATH, embeddings, allow_dangerous_deserialization=True)
    matches = vector_store.similarity_search(question, k=3)
    context = "\n\n".join([doc.page_content for doc in matches])

    # Xây dựng lịch sử hội thoại
    conversation = ""
    for turn in history:
        role = "User" if turn.type == 'user' else "Assistant"
        conversation += f"{role}: {turn.text}\n"

    # Tạo prompt đầy đủ
    prompt = f"""
You are a helpful assistant. 
Use the following conversation history and context to answer the question appropriately.

Context:
{context}

Conversation History:
{conversation}

Current Question:
{question}

Answer:
"""
    response = ask_huggingface(prompt)
    return response


def create_vectorstore_from_pdf(pdf_path: list[str]):
    text = ""

    for path in pdf_path:
        pdf_reader = PdfReader(path)
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
    
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n"],
        chunk_size=1000,
        chunk_overlap=150,
        length_function=len
    )
    chunks = text_splitter.split_text(text)

    vector_store = FAISS.from_texts(chunks, embeddings)
    vector_store.save_local(VECTOR_PATH)
 