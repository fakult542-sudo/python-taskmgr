from pathlib import Path

from taskmgr import Task, TaskManager, TaskStore, format_task


def make_manager(tmp_path: Path) -> TaskManager:
    return TaskManager(TaskStore(tmp_path / "tasks.json"))


def test_add_and_list(tmp_path: Path) -> None:
    manager = make_manager(tmp_path)

    first = manager.add("Write docs")
    second = manager.add("Ship release")

    tasks = manager.list_tasks()
    assert [task.id for task in tasks] == [1, 2]
    assert first.title == "Write docs"
    assert second.title == "Ship release"


def test_complete_and_pending_filter(tmp_path: Path) -> None:
    manager = make_manager(tmp_path)
    task = manager.add("Read email")

    manager.complete(task.id)

    all_tasks = manager.list_tasks(include_done=True)
    pending = manager.list_tasks(include_done=False)

    assert all_tasks[0].done is True
    assert pending == []


def test_remove_task(tmp_path: Path) -> None:
    manager = make_manager(tmp_path)
    manager.add("one")
    two = manager.add("two")

    removed = manager.remove(two.id)

    assert removed.title == "two"
    assert [task.title for task in manager.list_tasks()] == ["one"]


def test_format_task() -> None:
    task = Task(id=1, title="demo", done=False)
    assert format_task(task) == "[ ] 1: demo"
