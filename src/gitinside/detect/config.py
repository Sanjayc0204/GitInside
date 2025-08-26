# DetectorConfig dataclass (patterns, allowlists)
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass(frozen=True)
class DetectorConfig:
    default_python: str = "3.11"
    max_walk_depth: int = 8
    norecursedirs: List[str] = (".*", "build", "dist", ".venv", "venv", "env", "node_modules")
    default_testpaths: List[str] = ()                                                               # empty -> repo root
    default_python_files: List[str] = ("test_*.py", "*_test.py")
    apt_allowlist: Dict[str, List[str]] = None                                                      # pkg name -> apt pkgs