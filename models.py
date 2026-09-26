from pydantic import BaseModel
from typing import Optional

class Pokemon(BaseModel):
    id: int
    name: str
    type1: str
    type2: Optional[str]
    evolution: Optional[str]
    image_url: str
