import json
from fastapi import APIRouter, HTTPException
from jsql import sql
from utility.context import request_global, g
from typing import List, Optional

from ..model.Task import Task
from ..model.Todo import Todo


retrieve = APIRouter(prefix="/tasks",tags=["Tasks"])


@retrieve.post("/get/tasks", response_model=List[Task.Object])
def get_tasks(filter:Task.Filter): 
   
    tasks = sql(g().conn,
        '''
            SELECT 
                *
            FROM 
                tasks
            WHERE True 
                {% if id %}             AND id = :id                    {% endif %}
                {% if title %}          AND title LIKE "%{{title}}%"    {% endif %}
                {% if description %}    AND description = :description  {% endif %}
                {% if is_archived %}    AND archived = :is_archived     {% endif %}
                
        ''',**filter.dict()).dicts()

    return tasks

@retrieve.post("/get/todos", response_model=List[Todo.Object])
def get_todos(filter:Todo.Filter):
    todos = sql(g().conn,
        '''
            SELECT 
                *
            FROM 
                todos
            WHERE TRUE
                {% if id %}             AND id = :id                  {% endif %}
                {% if task_id %}        AND task_id = :task_id        {% endif %}
                {% if text %}           AND text LIKE "%{{text}}%"    {% endif %}
                {% if is_pinned %}      AND pinned = :is_pinned       {% endif %}
                {% if is_archived %}    AND archived = :is_archived   {% endif %}
                
        ''',**filter.dict()).dicts()
    return todos
