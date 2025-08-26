# Plan / DepsInfo / TestsInfo Dataclasses (+ plan hash)
from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass(frozen=True)
class DepsInfo:
    kind: str                                                               # "pyproject" | "poetry" | "venv" | "conda"
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
    runner: str                                                             # "pytest" | "tox" | "nosetests"
    deps: DepsInfo
    tests: TestsInfo
    env: Dict[str, str]                                                     # environment variables
    apt: List[str]                                                          # from allowlist map
    junit_xml: str = "/app/test-report.xml"                                 # path to junit xml
    pytest_args: str = "-q --maxfail=1 --disable-warnings -duration=10"     # pytest args




