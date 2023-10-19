from pydantic import BaseModel
from typing import List, Optional

class StartModel(BaseModel):
    quantity: int
    interval: int
