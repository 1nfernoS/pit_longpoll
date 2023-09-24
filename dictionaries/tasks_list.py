import datetime as dt

from ORM import Task, session
from tasks import bill, bill2, elites, siege


def init_tasks() -> None:
    task_list = session().query(Task).all()
    task_list_names = [t.task_target for t in task_list]

    now = dt.datetime.now()
    next_month = (now.month + 12) % 12 + 1
    next_siege = now + dt.timedelta(days=((7 + 3 - now.weekday()) % 7 - 1) if now.isoweekday() == 3 else 7)
    CONST_TASKS = (
        Task(now.replace(day=15, month=next_month, hour=0, minute=0, second=0, tzinfo=None), bill, is_regular=True),
        Task(now.replace(day=1, month=next_month, hour=0, minute=0, second=0, tzinfo=None), bill2, is_regular=True),
        Task(now.replace(day=2, month=next_month, hour=12, minute=30, second=0, tzinfo=None), elites, is_regular=True),
        Task(next_siege.replace(hour=23, minute=30, second=0, tzinfo=None), siege, is_regular=True)  # siege (remind)
        # TODO: Add message board (remind)
    )

    for task in CONST_TASKS:
        if task.task_target not in task_list_names:
            task.add()

    print("All Tasks successfully checked")

    return
