# Plan / DepsInfo / TestsInfo Dataclasses (+ plan hash)
from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass(frozen=True)
class DepsInfo:
    kind: str                                                               # "pyproject" | "requirements"
    path: str                                                               # relative path to pyproject.toml, poetry.lock, venv, or conda environment
    python: str                                                             # python version, e.g. "3.12"
    constraints: Optional[str] = None                                       # constraints
    extra_index_url: Optional[str] = None                                   # extra index url

@dataclass(frozen=True)
class TestsInfo:
    paths: List[str]                                                        # roots to pass to pytest
    files: List[str]                                                        # matched files (relative path)
    patterns: List[str]                                                     # effective python_files patterns
    config_source: Optional[str] = None                                     # path to pytest.ini, tox.ini, or nosetests.xml
    warnings: List[str] = field(default_factory=list)                       # warnings

@dataclass(frozen=True)
class Plan:
    runner: str
    deps: DepsInfo
    tests: TestsInfo
    env_allowed: List[str]
    python_tag: str
    work_dir: str
    dockerfile_template: str
    artifacts: Dict[str, str]
    limits: Dict[str, str]
    network_policy: str
    tests_mode: str
    apt: List[str]
    diagnostics: List[str]
    junit_xml: str = "/results/test-report.xml"
    pytest_args: str = "-q --maxfail=1 --disable-warnings"
    schema_version: int = 1
    plan_hash: str = ""




