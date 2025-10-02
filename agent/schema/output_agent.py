from pydantic import BaseModel
from typing import List

class Question(BaseModel):
      question:str
      aswers: List[str]
      correct_answer: str


class Test(BaseModel):
    result: List[Question]
