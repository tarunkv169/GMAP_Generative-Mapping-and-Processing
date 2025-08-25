import os
import json
from typing import List

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv

from langchain.chains import LLMChain, RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, YoutubeLoader
from langchain_community.vectorstores import FAISS

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise RuntimeError("Missing GOOGLE_API_KEY in environment")

app = FastAPI()

origins = ["http://localhost:5173","http://127.0.0.1:5173","http://localhost:3000","http://127.0.0.1:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

docs = None
vector_store = None
DOC_TEXT = ""

def process_documents(files: List[UploadFile] = None, youtube_url: str = None):
    global docs, vector_store, DOC_TEXT

    all_docs = []
    DOC_TEXT = ""

    if files:
        for file in files:
            file_extension = file.filename.split(".")[-1].lower()
            file_path = f"temp_{file.filename}"
            with open(file_path, "wb") as buffer:
                buffer.write(file.file.read())

            loader = None
            if file_extension == "pdf":
                loader = PyPDFLoader(file_path)
            elif file_extension in ["doc", "docx"]:
                loader = Docx2txtLoader(file_path)
            elif file_extension == "txt":
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    DOC_TEXT += f.read() + "\n"
            else:
                os.remove(file_path)
                raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_extension}")

            if loader:
                all_docs.extend(loader.load())
            os.remove(file_path)

    if youtube_url:
        try:
            loader = YoutubeLoader.from_youtube_url(youtube_url, add_video_info=True)
            all_docs.extend(loader.load())
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to load YouTube transcript: {e}")

    if all_docs:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        split_docs = text_splitter.split_documents(all_docs)
        DOC_TEXT = " ".join([doc.page_content for doc in split_docs])
        vector_store_local = FAISS.from_documents(split_docs, embeddings)
        # assign globals after successful creation
        globals()['docs'] = split_docs
        globals()['vector_store'] = vector_store_local
        return True

    if DOC_TEXT.strip():
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        split_docs = text_splitter.create_documents([DOC_TEXT])
        vector_store_local = FAISS.from_documents(split_docs, embeddings)
        globals()['docs'] = split_docs
        globals()['vector_store'] = vector_store_local
        return True

    return False

@app.post("/upload-docs")
async def upload_documents(files: List[UploadFile] = File(None), youtube_url: str = Form(None)):
    if not files and not youtube_url:
        raise HTTPException(status_code=400, detail="Please provide at least one document file or a YouTube URL.")
    ok = process_documents(files, youtube_url)
    if ok:
        return {"message": "Documents processed successfully."}
    raise HTTPException(status_code=500, detail="Failed to process documents.")

@app.get("/generate-mindmap")
async def generate_mindmap():
    if not DOC_TEXT.strip():
        raise HTTPException(status_code=400, detail="No documents processed. Please upload documents first.")

    mindmap_prompt_template = """
You are a structured JSON generator.
Based on the following document text, generate a mind map in pure JSON.
Return ONLY valid JSON with keys: name, children. No prose.

Document Text:
{text}

Format:
{{
  "name": "Main Topic",
  "children": [
    {{
      "name": "Subtopic 1",
      "children": [
        {{ "name": "Detail 1" }},
        {{ "name": "Detail 2" }}
      ]
    }},
    {{
      "name": "Subtopic 2",
      "children": []
    }}
  ]
}}
"""
    prompt = PromptTemplate(template=mindmap_prompt_template, input_variables=["text"])
    chain = LLMChain(llm=llm, prompt=prompt)

    try:
        response = chain.run(text=DOC_TEXT)
        # sanitize to extract JSON
        json_str = response.strip().strip("```")
        data = json.loads(json_str)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate mind map: {e}")

@app.get("/generate-quiz")
async def generate_quiz():
    if not DOC_TEXT.strip():
        raise HTTPException(status_code=400, detail="No documents processed. Please upload documents first.")

    quiz_prompt_template = """
You are a structured JSON generator.
Generate a multiple-choice quiz as a JSON array. Return ONLY JSON.
Each item must include: question (string), options (array of 4 strings), correctAnswer (string, one of options).

Document Text:
{text}

Example:
[
  {{
    "question": "What is the main topic?",
    "options": ["A","B","C","D"],
    "correctAnswer": "A"
  }}
]
"""
    prompt = PromptTemplate(template=quiz_prompt_template, input_variables=["text"])
    chain = LLMChain(llm=llm, prompt=prompt)

    try:
        response = chain.run(text=DOC_TEXT)
        json_str = response.strip().strip("```").replace("json", "").strip()
        quiz_data = json.loads(json_str)
        # basic validation
        if not isinstance(quiz_data, list):
            raise ValueError("Quiz is not a JSON array")
        return quiz_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate quiz: {e}")

@app.post("/ask-question")
async def ask_question(question: str = Form(...)):
    if not globals().get('vector_store'):
        raise HTTPException(status_code=400, detail="No documents processed. Please upload documents first.")

    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    rag_prompt_template = """
You are a helpful assistant. Use the following context to answer the question.
If you don't know, say you don't know.

Context:
{context}

Question: {question}
Answer:
"""
    rag_prompt = PromptTemplate(template=rag_prompt_template, input_variables=["context", "question"])

    # Build a chain that injects retrieved context into the prompt
    try:
        # Retrieve docs and format context
        docs = retriever.get_relevant_documents(question)
        context = "\n\n".join([d.page_content for d in docs])

        chain = LLMChain(llm=llm, prompt=rag_prompt)
        answer = chain.run(context=context, question=question)
        return {"answer": answer.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to answer question: {e}")
