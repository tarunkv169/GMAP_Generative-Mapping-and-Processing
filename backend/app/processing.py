from langchain_community.document_loaders import PyPDFLoader, UnstructuredWordDocumentLoader, YoutubeLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from youtube_transcript_api import YouTubeTranscriptApi
from langchain.docstore.document import Document
from typing import List

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

def load_pdf(file_path) -> List[Document]:
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    return splitter.split_documents(docs)

def load_docx(file_path) -> List[Document]:
    loader = UnstructuredWordDocumentLoader(file_path)
    docs = loader.load()
    return splitter.split_documents(docs)

def load_text(text_string, metadata=None) -> List[Document]:
    doc = Document(page_content=text_string, metadata=metadata or {})
    return splitter.split_documents([doc])

def load_youtube_transcript(video_url) -> List[Document]:
    try:
        loader = YoutubeLoader.from_youtube_url(video_url)
        docs = loader.load()
    except Exception:
        # fallback using youtube_transcript_api
        video_id = video_url.split("v=")[-1].split("&")[0]
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        s = "\n".join([f"[{t['start']:.0f}] {t['text']}" for t in transcript_list])
        docs = [Document(page_content=s, metadata={"source": video_url})]
    return splitter.split_documents(docs)
