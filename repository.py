from database import get_connection


def get_all_tasks():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, title, done FROM tasks ORDER BY id"
            )
            rows = cursor.fetchall()

    return [
        {
            "id": row[0],
            "title": row[1],
            "done": row[2]
        }
        for row in rows
    ]


def get_task_by_id(task_id: int):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, title, done FROM tasks WHERE id = %s",
                (task_id,)
            )
            row = cursor.fetchone()

    if row is None:
        return None

    return {
        "id": row[0],
        "title": row[1],
        "done": row[2]
    }


def create_task(title: str, done: bool):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO tasks (title, done)
                VALUES (%s, %s)
                RETURNING id, title, done
                """,
                (title, done)
            )
            row = cursor.fetchone()

        connection.commit()

    return {
        "id": row[0],
        "title": row[1],
        "done": row[2]
    }


def update_task(task_id: int, title: str, done: bool):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE tasks
                SET title = %s, done = %s
                WHERE id = %s
                RETURNING id, title, done
                """,
                (title, done, task_id)
            )
            row = cursor.fetchone()

        connection.commit()

    if row is None:
        return None

    return {
        "id": row[0],
        "title": row[1],
        "done": row[2]
    }


def delete_task(task_id: int):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM tasks WHERE id = %s",
                (task_id,)
            )
            deleted = cursor.rowcount > 0

        connection.commit()

    return deleted