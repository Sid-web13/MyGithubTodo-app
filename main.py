
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import sqlite3
from pathlib import Path

app = FastAPI()

# File locations
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "todo.db"

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static"
)


# DATABASE CONNECTION
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# CREATE DATABASE TABLE
def create_table():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


create_table()


# 1. READ TASKS
@app.get("/")
def home(request: Request):

    conn = get_db()

    tasks = conn.execute(
        "SELECT * FROM tasks ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"tasks": tasks}
    )


# 2. CREATE TASK
@app.post("/add")
def add_task(title: str = Form(...)):

    title = title.strip()

    if title:
        conn = get_db()

        conn.execute(
            "INSERT INTO tasks (title) VALUES (?)",
            (title,)
        )

        conn.commit()
        conn.close()

    return RedirectResponse("/", status_code=303)


# 3. UPDATE TASK STATUS
@app.post("/toggle/{task_id}")
def toggle_task(task_id: int):

    conn = get_db()

    conn.execute("""
        UPDATE tasks
        SET completed = 1 - completed
        WHERE id = ?
    """, (task_id,))

    conn.commit()
    conn.close()

    return RedirectResponse("/", status_code=303)


# 4. DELETE TASK
@app.post("/delete/{task_id}")
def delete_task(task_id: int):

    conn = get_db()

    conn.execute(
        "DELETE FROM tasks WHERE id = ?",
        (task_id,)
    )

    conn.commit()
    conn.close()

    return RedirectResponse("/", status_code=303)
