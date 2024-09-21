from pydantic import BaseModel


class Tweet(BaseModel):
    text: str
    
class XSendTweetRequest(BaseModel):
    text: str