from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Match:
    line:str
    text:str
    page: Optional[str] = None

@dataclass
class DeepSearchDocument:
    id:int
    filename:str
    department_name:str
    uploaded_at:str
    category:str
    file_url:str

    matches: list[Match]