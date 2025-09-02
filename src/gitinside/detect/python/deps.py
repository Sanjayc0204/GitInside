# detect_deps(root, cfg) -> DepsInfo, Diagnostics
from pathlib import Path
from typing import Tuple, List
from ..plan import DepsInfo
from ..config import DetectorConfig
import tomllib
from typing import Optional

def _choose_reqs(root: Path) -> Optional[Path]:
    candidates = list(root.glob("requirements*.txt"))

    if not candidates:
        return None
    preferred = ["requirements.lock", "requirements-freeze.txt", "requirements-prod.txt", "requirements.txt"]

    for name in preferred:
        for p in candidates:
            if p.name.lower() == name:
                return p

    return sorted(candidates, key=lambda p: (len(p.name), p.name))[0]

def _get_python_version_from_pyproject_toml(reqfile: Path) -> Optional[str]:
    try:
        data = tomllib.loads(reqfile.read_text(encoding="utf-8"))
    except Exception:
        return None
    req = (data.get("project") or {}).get("requires-python")
    if not req:
        req = (
            data.get("tool", {})
                .get("poetry", {})
                .get("dependencies", {})
                .get("python")
        )
    if not req:
        return None
    return req


def detect_deps(root: Path, cfg: DetectorConfig) -> Tuple[DepsInfo, List[str]]:
    diags = []

    pyproject_toml = root / "pyproject.toml"
    
    if pyproject_toml.exists():
        diags.append(f"Using pyproject.toml: {pyproject_toml}")
        version = _get_python_version_from_pyproject_toml(pyproject_toml)
        if version:
            diags.append(f"Python version: {version}")
        else:
            diags.append("No python version found in pyproject.toml; using default python version: " + cfg.default_python)
            version = cfg.default_python

        return (DepsInfo(
            kind = "pyproject",
            path = "pyproject.toml",
            python = version,
        ), diags)
    
    reqfile = _choose_reqs(root)
    if reqfile:
        diags.append(f"Using requirements file: {reqfile}")
        return (DepsInfo(
            kind = "python-requirements-pytest",
            path = reqfile.name,
            python = cfg.default_python,
        ), diags)
    
    diags.append("No pyproject.toml or requirements file found" + cfg.default_python)

    return (DepsInfo(
        kind = "python-requirements-pytest",
        path = "requirements.txt",
        python = cfg.default_python,
    ), diags)

    

            
        

