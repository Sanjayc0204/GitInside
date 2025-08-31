import pytest
from pathlib import Path
from gitinside.detect.plan import DepsInfo, TestsInfo
from gitinside.detect.compose import compose_plan

def test_compose_plan_with_pyproject():
    deps = DepsInfo(
        kind="pyproject",
        python=">=3.8,<3.12",
        path="pyproject.toml"
    )
    tests = TestsInfo(paths=["tests"],  files=["test.py"], patterns=["test"])
    
    plan = compose_plan(Path("."), deps, tests)
    assert plan.python_tag == "3.8-slim"
    assert plan.dockerfile_template == "python-pyproject-pytest"

def test_compose_plan_with_requirements():
    deps = DepsInfo(
        kind="requirements",
        python="3.10",
        path="requirements.txt"
    )
    # ... similar assertions
    tests = TestsInfo(paths=["tests"], files=["test.py"], patterns=["test"])
    
    plan = compose_plan(Path("."), deps, tests)
    assert plan.python_tag == "3.10-slim"
    assert plan.dockerfile_template == "python-requirements-pytest"