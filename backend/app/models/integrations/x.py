from pydantic import BaseModel


class Tweet(BaseModel):
    id: str
    text: str
    
class XSendTweetRequest(BaseModel):
    text: str