import datetime as dt

from ORM import Task, session
from .exec_task import bill, bill2, elites, siege


def init_tasks() -> None:
    with session() as s:
        task_list = s.query(Task).all()
    task_list_names = [t.task_target for t in task_list]

    now = dt.datetime.utcnow() + dt.timedelta(hours=3)
    next_month = now.month % 12 + 1
    next_siege = now + dt.timedelta(days=(7 + 3 - now.isoweekday()) % 7)
    CONST_TASKS = (
        Task(now.replace(day=15, month=next_month, hour=10, minute=30, second=0, tzinfo=None), bill, is_regular=True),
        Task(now.replace(day=1, month=next_month, hour=10, minute=30, second=0, tzinfo=None), bill2, is_regular=True),
        Task(now.replace(day=2, month=next_month, hour=12, minute=30, second=0, tzinfo=None), elites, is_regular=True),
        Task(next_siege.replace(hour=22, minute=5, second=0), siege, is_regular=True)
        # TODO: Add message board (remind)
    )

    for task in CONST_TASKS:
        if task.task_target not in task_list_names:
            task.add()

    print("All Tasks successfully checked")

    return
