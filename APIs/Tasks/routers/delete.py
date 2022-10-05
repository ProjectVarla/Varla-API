import json
from fastapi import APIRouter, HTTPException
from jsql import sql
from utility.context import request_global, g
from typing import List, Optional

from ..model.Task import Task
from ..model.Todo import Todo


delete = APIRouter(prefix="/tasks",tags=["Tasks"])

@delete.delete("/delete/task/{task_id}", response_model=int)
def delete_task(task_id:int):    
    deleted_count = sql(g().conn,
        '''
            
            DELETE FROM tasks WHERE id = :task_id 

        ''',task_id = task_id).rowcount
    return deleted_count

@delete.delete("/delete/todo/{todo_id}", response_model=int)
def delete_todo(todo_id:int): 
    deleted_count = sql(g().conn,
        '''

            DELETE FROM todos WHERE id = :todo_id 

        ''',todo_id = todo_id).rowcount

    return deleted_count
