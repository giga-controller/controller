from typing import Optional
from pydantic import BaseModel, Field

class Docs(BaseModel):
    id: str
    title: str
    content: Optional[str]
    

class DocsCreateRequest(BaseModel):
    content: Optional[str] = Field(description="Content to insert into the document, if any")

class DocsFilterRequest(BaseModel): 
    id: list[str] = Field(description="Document id to filter documents with")
    
class DocsGetRequest(DocsFilterRequest):
    pass

class DocsUpdateRequest(DocsFilterRequest):
    updated_content: str = Field(description="Updated content to replace the document with")

class DocsDeleteRequest(DocsFilterRequest):
    pass