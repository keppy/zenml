import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from requests.auth import HTTPBasicAuth

PRIORITIES = {"LOW": 4, "MEDIUM": 3, "HIGH": 2}


GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_REPOSITORY = os.environ["GITHUB_REPOSITORY"]
GITHUB_REF = os.environ["GITHUB_REF"]

JIRA_BASE_URL = os.environ["JIRA_BASE_URL"]
JIRA_USERNAME = os.environ["JIRA_USERNAME"]
JIRA_API_TOKEN = os.environ["JIRA_API_TOKEN"]

JIRA_BOARD_ID = os.environ["JIRA_BOARD_ID"]
JIRA_ISSUE_TYPE_ID = os.environ["JIRA_ISSUE_TYPE_ID"]


class Todo:
    def __init__(
        self,
        filepath: str,
        description: str,
        priority: Optional[str] = None,
        issue_key: Optional[str] = None,
    ):
        self.filepath = filepath
        self.description = description
        self.priority = priority
        self.issue_key = issue_key


def issue_payload_for_todo(todo: Todo) -> Dict[str, Any]:
    description = (
        f"Automatically generated from TODO comment in {todo.filepath}."
    )
    return {
        "fields": {
            "summary": todo.description,
            "issuetype": {"id": f"{JIRA_ISSUE_TYPE_ID}"},
            "project": {"id": f"{JIRA_BOARD_ID}"},
            "priority": {"id": f"{PRIORITIES[todo.priority]}"},
            "labels": [],
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"text": description, "type": "text"}],
                    }
                ],
            },
        },
    }


def create_jira_issues(todos: List[Todo]):
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/bulk"
    auth = HTTPBasicAuth(JIRA_USERNAME, JIRA_API_TOKEN)
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    payload = json.dumps(
        {"issueUpdates": [issue_payload_for_todo(todo) for todo in todos]}
    )

    response = requests.request(
        "POST", url, data=payload, headers=headers, auth=auth
    )

    issues = json.loads(response.text)["issues"]
    for todo, issue in zip(todos, issues):
        todo.issue_key = issue["key"]


def find_unreferenced_todos(file: Path) -> List[Todo]:
    file_content = file.read_text()
    matches = re.findall(
        r"^\s*# TODO ?\[(LOW|MEDIUM|HIGH)\] ?:(.*$\n(^\s*# {2}.*$\n)*)",
        file_content,
        flags=re.MULTILINE,
    )

    todos = []
    for priority, description, _ in matches:
        # remove whitespace and leading '#' from description
        lines = description.split("\n")
        lines = [line.strip().lstrip("#").strip() for line in lines]
        description = " ".join(lines)

        todos.append(
            Todo(filepath=str(file), description=description, priority=priority)
        )

    return todos


def push_files(files: List[str]):
    files = " ".join(files)
    subprocess.run(f"git add {files}", shell=True)
    subprocess.run(
        f"git commit --no-verify -m 'Update TODO references'", shell=True
    )
    subprocess.run(
        f'git push "https://x-access-token:{GITHUB_TOKEN}@github.com'
        f'/{GITHUB_REPOSITORY}.git" HEAD:"{GITHUB_REF}"'
    )


def update_files_with_issue_keys(file: Path, todos: List[Todo]):
    file_content = file.read_text()
    todo_iterator = iter(todos)

    def _replace(match):
        todo = next(todo_iterator)
        result = match.group(1) + f"{todo.issue_key}" + match.group(3)
        return result

    new_file_content = re.sub(
        r"(\s*# TODO ?\[)(LOW|MEDIUM|HIGH)(\] ?:)",
        _replace,
        file_content,
        re.MULTILINE,
    )

    file.write_text(new_file_content)


def update_todo_references():
    zenml_root = Path("src/zenml")
    # test_root = Path("tests")
    # python_files = itertools.chain(
    #     zenml_root.rglob("*.py"), test_root.rglob("*.py")
    # )
    python_files = zenml_root.rglob("*.py")

    modified_files = []
    for file in python_files:
        todos = find_unreferenced_todos(file)

        if todos:
            create_jira_issues(todos)
            update_files_with_issue_keys(file, todos)
            modified_files += [todo.filepath for todo in todos]

            # TODO: remove this once we're sure the script works
            break

    push_files(modified_files)


if __name__ == "__main__":
    print(GITHUB_REPOSITORY)
    print(GITHUB_REF)
    print(JIRA_BASE_URL)
    print(JIRA_BOARD_ID)

    # update_todo_references()
