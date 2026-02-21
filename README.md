# python-taskmgr

A tiny Python CLI task manager that stores tasks in JSON.

## Usage

```bash
python taskmgr.py add "buy milk"
python taskmgr.py list
python taskmgr.py done 1
python taskmgr.py list --pending
python taskmgr.py remove 1
```

Use a custom database file:

```bash
python taskmgr.py --db ./tasks.json add "write tests"
```

## Run tests

```bash
python -m pytest
```
