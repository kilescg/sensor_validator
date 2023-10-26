from pydantic import BaseModel
from typing import List, Optional

class StartModel(BaseModel):
    total_round: int
    interval: int
