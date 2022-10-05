import json
from fastapi import APIRouter, HTTPException
from jsql import sql
from utility.context import request_global, g
from typing import List, Optional

from ..model import Task,Todo

update = APIRouter(prefix="/tasks",tags=["Tasks"])



@update.put("/update/task/{task_id}", response_model=int)
def edit_task(task_id :int ,edit_task:Task.Edit):

    if not len(edit_task.dict(exclude_unset=True)):
        raise Task.Exceptions.NoUpdateParamatersException()
        
    updated_count = sql(g().conn,
    '''
        UPDATE
            `tasks`
        SET 
            {% with counter = 0 %}
                {% if title %}          {% if counter %},{% endif %}{% set counter = counter + 1 %}    title=:title                 {% endif %}
                {% if description %}    {% if counter %},{% endif %}{% set counter = counter + 1 %}    description=:description     {% endif %}
                {% if color %}          {% if counter %},{% endif %}{% set counter = counter + 1 %}    color=:color                 {% endif %}
                {% if archived %}       {% if counter %},{% endif %}{% set counter = counter + 1 %}    archived=:archived           {% endif %}  
            {% endwith %}
        WHERE id = :task_id
    '''
    ,task_id = task_id,**edit_task.dict(exclude_unset=True)).rowcount
    
    return updated_count

@update.put("/update/todo/{todo_id}", response_model=int)
def edit_todo(todo_id:int,edit_todo:Todo.Edit): 
    
    if not len(edit_todo.dict(exclude_unset=True)):
        raise Todo.Exceptions.NoUpdateParamatersException()
        
    updated_count = sql(g().conn,
    '''
        UPDATE
            `todos`
        SET 
            {% with counter = 0 %}
                {% if text %}        {% if counter %},{% endif %}{% set counter = counter + 1 %}    text=:text              {% endif %}
                {% if checked %}     {% if counter %},{% endif %}{% set counter = counter + 1 %}    checked=:checked        {% endif %}
                {% if archived %}    {% if counter %},{% endif %}{% set counter = counter + 1 %}    archived=:archived      {% endif %}
                {% if pinned %}      {% if counter %},{% endif %}{% set counter = counter + 1 %}    pinned=:pinned          {% endif %}  
            {% endwith %}
        WHERE id = :todo_id
    '''
    ,todo_id = todo_id,**edit_todo.dict(exclude_unset=True)).rowcount
    
    return updated_count

