from pydantic import BaseModel
from typing import Optional

class UploadResponse(BaseModel):
    success: bool
    message: str

class MapRequest(BaseModel):
    query: Optional[str] = "Create a concept map of the uploaded documents"
    top_k: Optional[int] = 8
