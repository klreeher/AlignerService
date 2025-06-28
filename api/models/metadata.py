from pydantic import BaseModel, HttpUrl, Field
from typing import Optional

class Metadata(BaseModel):
    title: str = Field(..., description="Title of the work")
    subtitle: Optional[str] = Field(None, description="Subtitle of the work")
    author: str = Field(..., description="Author of the work")
    description: Optional[str] = Field(None, description="Description or notes")
    narrator: Optional[str] = Field(None, description="Narrator's name")
    contributor: Optional[str] = Field(None, description="Contributor's name")
    original_url: Optional[HttpUrl] = Field(None, description="Original work URL")
    fandom: Optional[str] = Field(None, description="Fandom name(s)")
    publisher: Optional[str] = Field(None, description="Publisher")
