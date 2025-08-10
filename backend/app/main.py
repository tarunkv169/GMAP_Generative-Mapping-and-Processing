import os
import json
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from .processing import load_pdf, load_docx, load_text, load_youtube_transcript
from .vectorstore import create_or_get_vectorstore, load_vectorstore, get_embeddings
from .schemas import UploadResponse, MapRequest
from langchain.chains import RetrievalQA, LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload", response_model=UploadResponse)
async def upload(file: UploadFile = File(None), youtube_url: str = Form(None)):
    if youtube_url:
        docs = load_youtube_transcript(youtube_url)
        create_or_get_vectorstore(docs, collection_name="default")
        return {"success": True, "message": "YouTube transcript added"}
    if file:
        ext = (file.filename or "").lower()
        path = f"{UPLOAD_DIR}/{file.filename}"
        with open(path, "wb") as f:
            content = await file.read()
            f.write(content)
        if ext.endswith(".pdf"):
            docs = load_pdf(path)
        elif ext.endswith(".docx") or ext.endswith(".doc"):
            docs = load_docx(path)
        else:
            text = content.decode(errors="ignore")
            docs = load_text(text, metadata={"source": file.filename})
        create_or_get_vectorstore(docs, collection_name="default")
        return {"success": True, "message": f"Uploaded and indexed {file.filename}"}
    return {"success": False, "message": "No file or youtube_url provided"}

@app.post("/generate-map")
def generate_map(payload: MapRequest):
    embeddings = get_embeddings()
    vectordb = load_vectorstore(collection_name="default", embeddings=embeddings)
    retriever = vectordb.as_retriever(search_kwargs={"k": payload.top_k})

    # Instantiate Gemini LLM via langchain-google-genai
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-pro", temperature=0)

    # RetrievalQA: retrieve relevant chunks
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=False
    )
    context = qa_chain.run(payload.query)

    # Prompt: ask LLM to output nodes/edges JSON
    prompt = PromptTemplate(
        input_variables=["context", "instruction"],
        template="""You are given contextual document chunks delimited by triple backticks:
```{context}```
Task: {instruction}

Return: a JSON object with:
"nodes": [{ "id": "n1", "label": "short title", "details": "longer text" }],
"edges": [{ "from": "n1", "to": "n2", "label": "relation" }]

Only valid JSON. No extra text.
"""
    )

    chain = LLMChain(llm=llm, prompt=prompt)
    json_out = chain.run({"context": context, "instruction": payload.query})
    try:
        parsed = json.loads(json_out)
    except Exception:
        # Retry with stricter instruction
        json_out = chain.run({"context": context, "instruction": payload.query + " Output only valid JSON, nothing else."})
        parsed = json.loads(json_out)
    return {"map": parsed}
