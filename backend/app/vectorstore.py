import os
from langchain.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")

def get_embeddings():
    # Embedding model name may vary; "models/embedding-001" is a common name
    return GoogleGenerativeAIEmbeddings(model="models/embedding-001")

def create_or_get_vectorstore(docs, embeddings=None, collection_name="default"):
    if embeddings is None:
        embeddings = get_embeddings()
    vectordb = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name=collection_name,
        persist_directory=PERSIST_DIR
    )
    vectordb.persist()
    return vectordb

def load_vectorstore(collection_name="default", embeddings=None):
    if embeddings is None:
        embeddings = get_embeddings()
    return Chroma(
        collection_name=collection_name,
        persist_directory=PERSIST_DIR,
        embedding_function=embeddings
    )
