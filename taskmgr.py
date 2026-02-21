#!/usr/bin/env python3
"""Simple local task manager CLI."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

DEFAULT_DB_PATH = Path.home() / ".taskmgr.json"


@dataclass
class Task:
    id: int
    title: str
    done: bool = False


class TaskStore:
    def __init__(self, path: Path = DEFAULT_DB_PATH):
        self.path = path

    def load(self) -> list[Task]:
        if not self.path.exists():
            return []
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        return [Task(**item) for item in raw]

    def save(self, tasks: Iterable[Task]) -> None:
        serializable = [asdict(task) for task in tasks]
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(serializable, indent=2), encoding="utf-8")


class TaskManager:
    def __init__(self, store: TaskStore):
        self.store = store

    def add(self, title: str) -> Task:
        tasks = self.store.load()
        next_id = max((task.id for task in tasks), default=0) + 1
        task = Task(id=next_id, title=title)
        tasks.append(task)
        self.store.save(tasks)
        return task

    def list_tasks(self, *, include_done: bool = True) -> list[Task]:
        tasks = self.store.load()
        if include_done:
            return tasks
        return [task for task in tasks if not task.done]

    def complete(self, task_id: int) -> Task:
        tasks = self.store.load()
        for task in tasks:
            if task.id == task_id:
                task.done = True
                self.store.save(tasks)
                return task
        raise ValueError(f"Task {task_id} not found")

    def remove(self, task_id: int) -> Task:
        tasks = self.store.load()
        for idx, task in enumerate(tasks):
            if task.id == task_id:
                removed = tasks.pop(idx)
                self.store.save(tasks)
                return removed
        raise ValueError(f"Task {task_id} not found")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="taskmgr", description="Manage tasks from the command line")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH, help="Path to task database JSON file")

    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("title", help="Task title")

    list_parser = subparsers.add_parser("list", help="List tasks")
    list_parser.add_argument("--pending", action="store_true", help="Only show pending tasks")

    complete_parser = subparsers.add_parser("done", help="Mark a task as completed")
    complete_parser.add_argument("task_id", type=int, help="ID of the task to complete")

    remove_parser = subparsers.add_parser("remove", help="Delete a task")
    remove_parser.add_argument("task_id", type=int, help="ID of the task to remove")

    return parser


def format_task(task: Task) -> str:
    state = "x" if task.done else " "
    return f"[{state}] {task.id}: {task.title}"


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    manager = TaskManager(TaskStore(args.db))

    try:
        if args.command == "add":
            task = manager.add(args.title)
            print(f"Added task {task.id}: {task.title}")
            return 0

        if args.command == "list":
            tasks = manager.list_tasks(include_done=not args.pending)
            if not tasks:
                print("No tasks found.")
                return 0
            for task in tasks:
                print(format_task(task))
            return 0

        if args.command == "done":
            task = manager.complete(args.task_id)
            print(f"Completed task {task.id}: {task.title}")
            return 0

        if args.command == "remove":
            task = manager.remove(args.task_id)
            print(f"Removed task {task.id}: {task.title}")
            return 0

        parser.error("Unknown command")
        return 2
    except ValueError as exc:
        print(exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
