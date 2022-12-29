from typing import List

from fastapi import APIRouter
from jsql import sql
from Models import Task, Todo

from Utility.context import g

retrieve = APIRouter(prefix="/tasks", tags=["Tasks"])


@retrieve.post("/get/tasks", response_model=List[Task.Object])
def get_tasks(filter: Task.Filter):

    tasks = sql(
        g().conn,
        """
            SELECT 
                *
            FROM 
                tasks
            WHERE True 
                {% if id %}             AND id = :id                    {% endif %}
                {% if title %}          AND title LIKE "%{{title}}%"    {% endif %}
                {% if description %}    AND description = :description  {% endif %}
                AND archived = :is_archived
        """,
        **filter.dict()
    ).dicts()

    return tasks


@retrieve.post("/get/todos", response_model=List[Todo.Object])
def get_todos(filter: Todo.Filter):
    todos = sql(
        g().conn,
        """
            SELECT 
                *
            FROM 
                todos
            WHERE TRUE
                {% if id %}             AND id = :id                  {% endif %}
                {% if task_id %}        AND task_id = :task_id        {% endif %}
                {% if text %}           AND text LIKE "%{{text}}%"    {% endif %}
                {% if is_pinned %}      AND pinned = :is_pinned       {% endif %}
                AND archived = :is_archived 
        """,
        **filter.dict()
    ).dicts()
    return todos
