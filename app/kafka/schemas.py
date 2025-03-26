from pydantic import EmailStr, BaseModel
from typing import Optional
import json
from datetime import datetime


class EmailVerificationMessage(BaseModel):
    email: EmailStr
    username: str
    user_id: int
    time_start: Optional[str] = None
    verify_email: str
    

    def to_json(self):
        data = self.model_dump()
        data["time_start"] = datetime.now().isoformat()
        return json.dumps(data)
        
    @classmethod
    def from_join(cls, json_data):
        data = json.loads(json_data)
        return cls(**data)
    
