from pydantic import BaseModel
from datetime import datetime

class ActiveSession(BaseModel):
    id: int  # Add an ID field for the primary key
    username: str
    access_token: str
    expiry_time: datetime
