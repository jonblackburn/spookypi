# app/model.py

from pydantic import BaseModel, Field

class SpookyRequest(BaseModel):
    id: int = Field(default=None)
    content: str = Field(default=None)
    
    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "content":"",

            }
        }
    