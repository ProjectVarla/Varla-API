from pydantic import BaseModel
from typing import List, Optional,Union
from fastapi import HTTPException


class Task:
    class Base(BaseModel):
        title       :str
        description :str
        color       :str #TODO change to enum
        archived    :bool

    class Object(Base):
        id          :int

    class Edit(BaseModel):
        title       :Optional[str]
        description :Optional[str] 
        color       :Optional[str]  #TODO change to enum
        archived    :Optional[bool]  

    class Filter(BaseModel):
        id          :Optional[int] = 0
        title       :Optional[str] = ""
        description :Optional[str] = ""
        is_archived :Optional[bool] = False 

    class Exceptions:
        class NoUpdateParamatersException(HTTPException):
            """Exception raised when Not providing any update paramater"""
            def __init__(self):
                super().__init__(status_code=404, detail="No Update Paramater was found!")

            def __str__(self):
                return str(self.message)