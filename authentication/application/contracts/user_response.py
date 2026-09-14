from dataclasses import dataclass
from typing import Optional
from datetime import datetime
@dataclass
class UserResponseContract:

    id:int
    user_id:int
    username:str
    email:str
    role:str
    is_active:Optional [bool] = None
    is_staff:Optional[bool] = None
    last_login:Optional[datetime] = None

