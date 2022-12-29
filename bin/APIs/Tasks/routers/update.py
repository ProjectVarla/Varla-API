from fastapi import APIRouter, Response, status
from jsql import sql
from Models import Task, Todo

from Utility.context import g
from Models.Exceptions import NoUpdateParamatersException


update = APIRouter(prefix="/tasks", tags=["Tasks"])


@update.put("/update/task/{task_id}", response_model=int)
def edit_task(task_id: int, edit_task: Task.Edit, response: Response):

    data = {key: value for key, value in edit_task.dict().items() if value is not None}

    if not data:
        raise NoUpdateParamatersException()

    updated_count = sql(
        g().conn,
        """
            UPDATE
                `tasks`
            SET 
                {% with counter = 0 %}
                    {% if title %}                  {% if counter %},{% endif %}{% set counter = counter + 1 %}    title=:title                 {% endif %}
                    {% if description %}            {% if counter %},{% endif %}{% set counter = counter + 1 %}    description=:description     {% endif %}
                    {% if color %}                  {% if counter %},{% endif %}{% set counter = counter + 1 %}    color=:color                 {% endif %}
                    {% if archived != null %}       {% if counter %},{% endif %}{% set counter = counter + 1 %}    archived=:archived           {% endif %}  
                {% endwith %}
            WHERE id = :task_id
    """,
        task_id=task_id,
        **data
    ).rowcount

    return updated_count


@update.put("/update/todo/{todo_id}", response_model=int)
def edit_todo(todo_id: int, edit_todo: Todo.Edit):

    data = {key: value for key, value in edit_task.dict().items() if value is not None}

    if not data:
        raise NoUpdateParamatersException()

    updated_count = sql(
        g().conn,
        """
            UPDATE
                `todos`
            SET 
                {% with counter = 0 %}
                    {% if text != null     %}   {% if counter %},{% endif %}{% set counter = counter + 1 %}    text=:text              {% endif %}
                    {% if checked != null  %}   {% if counter %},{% endif %}{% set counter = counter + 1 %}    checked=:checked        {% endif %}
                    {% if archived != null %}   {% if counter %},{% endif %}{% set counter = counter + 1 %}    archived=:archived      {% endif %}
                    {% if pinned != null   %}   {% if counter %},{% endif %}{% set counter = counter + 1 %}    pinned=:pinned          {% endif %}  
                {% endwith %}
            WHERE id = :todo_id
    """,
        todo_id=todo_id,
        **edit_todo.dict(exclude_unset=True)
    ).rowcount

    return updated_count
