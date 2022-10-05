from typing import List, Optional, Union
from fastapi import HTTPException,status
from pydantic import BaseModel


class Todo:
    class Base(BaseModel):
        text        :str

    class Object(Base):
        id          :int
        task_id     :int
        archived    :bool
        pinned      :bool
        checked     :bool

    class Edit(BaseModel):
        text        :Optional[str]
        archived    :Optional[bool]
        pinned      :Optional[bool]
        checked     :Optional[bool]

    class Filter(BaseModel):
        id          :Union[int,None] 
        task_id     :Union[int,None] 
        text        :Union[str,None] = ""
        is_checked  :Union[bool,None] = False
        is_pinned   :Union[bool,None] = False
        is_archived :Union[bool,None] = False

    class Exceptions:
        class TaskIdForeignViolation(HTTPException):
            """Exception raised when Not task_id foreign key constraint violated"""
            def __init__(self):
                super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="task_id foreign key constraint violation!")

            def __str__(self):
                return str(self.message)

        class NoUpdateParamatersException(HTTPException):
            """Exception raised when Not providing any update paramater"""
            def __init__(self):
                super().__init__(status_code=404, detail="No Update Paramater was found!")

            def __str__(self):
                return str(self.message)