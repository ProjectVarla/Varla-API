import json
from fastapi import APIRouter, HTTPException, status
from jsql import sql
from utility.context import request_global, g
from typing import List, Optional

from ..model.Task import Task
from ..model.Todo import Todo
from sqlalchemy.exc import IntegrityError

insert = APIRouter(prefix="/tasks", tags=["Tasks"])


@insert.post("/insert/task", response_model=int, status_code=status.HTTP_201_CREATED)
def create_task(task: Task.Base):
    task_id = sql(g().conn,
        '''

        INSERT INTO `tasks` 
            (`title`, `description`, `color`) 
        VALUES 
            (:title, :description, :color)

        ''', **task.dict()).lastrowid
    return task_id


@insert.post("/insert/todo/{task_id}", response_model=int, status_code=status.HTTP_201_CREATED)
def create_todo(todo: Todo.Base, task_id: int):
    
    try:
        todo_id = sql(g().conn,
            '''

            INSERT INTO `todos` 
                (`task_id`,`text`)
            VALUES
                (:task_id,:text)
                    
            ''', task_id=task_id, **todo.dict()).lastrowid

    except IntegrityError:
        raise Todo.Exceptions.TaskIdForeignViolation()
    return todo_id
