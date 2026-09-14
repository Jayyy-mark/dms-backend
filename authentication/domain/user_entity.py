from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class UserEntity:
    id:int
    user_id:str
    username:str
    email:str
    role:str
    is_active:bool
    is_staff:bool
    last_login: Optional[datetime] = None
