# detect_tests(root, cfg) -> TestsInfo, Diagnostics.
import os
from pathlib import Path
from typing import Optional, Tuple, List
from ..plan import TestsInfo
from ..config import DetectorConfig
import configparser
import tomllib
import fnmatch

"""
Only checks for pytest.ini and pyproject.toml
"""


def _find_pytest(root: Path) -> Optional[Path]:
    for p in root.iterdir():
        if p.is_file() and p.name == "pytest.ini":
            return p
    return None

def _find_pyproject_toml(root: Path) -> Optional[Path]:
    for p in root.iterdir():
        if p.is_file() and p.name == "pyproject.toml":
            return p
    return None

def _parse_pytest_ini(pytest_ini: Path, cfg: DetectorConfig) -> Tuple[list[str], list[str], list[str], str]:
    config = configparser.ConfigParser()
    config.read(str(pytest_ini), encoding="utf-8")
    data = dict(config['pytest'] if 'pytest' in config else {})

    testpaths = data.get("testpaths", cfg.default_testpaths)
    python_files = data.get("python_files", cfg.default_python_files)
    norecursedirs = data.get("norecursedirs", cfg.norecursedirs)
    
    if isinstance(testpaths, str):
        testpaths = testpaths.split()
    if isinstance(python_files, str):
        python_files = python_files.split()
    if isinstance(norecursedirs, str):
        norecursedirs = norecursedirs.split()

    testpaths = list(testpaths)
    python_files = list(python_files)
    norecursedirs = list(norecursedirs)
    
    return testpaths, python_files, norecursedirs, "pytest.ini"
    

def _parse_pyproject_toml(pyproject_toml: Path, cfg: DetectorConfig) -> Tuple[list[str], list[str], list[str], str]:
    with open(pyproject_toml, "rb") as f:
        data = tomllib.load(f)
        ini = (
            data.get("tool", {})
                .get("pytest", {})
                .get("ini_options", {})
            or {}
        )

        testpaths      = ini.get("testpaths", cfg.default_testpaths)
        python_files   = ini.get("python_files", cfg.default_python_files)
        norecursedirs  = ini.get("norecursedirs", cfg.norecursedirs)

        if isinstance(testpaths, str):
            testpaths = testpaths.split()
        if isinstance(python_files, str):
            python_files = python_files.split()
        if isinstance(norecursedirs, str):
            norecursedirs = norecursedirs.split()

        testpaths = list(testpaths)
        python_files = list(python_files)
        norecursedirs = list(norecursedirs)

        return testpaths, python_files, norecursedirs, "pyproject.toml"
    
def _skip_dir(name: str, patterns: list[str]) -> bool:
    return name.startswith(".") or any(fnmatch.fnmatch(name, pat) for pat in patterns)

def detect_tests(root: Path, cfg: DetectorConfig) -> Tuple[TestsInfo, list[str]]:
    diags: list[str] = []
    test_files: list[str] = []

    pytest_ini = _find_pytest(root)
    pyproject_toml = _find_pyproject_toml(root)

    if pytest_ini:
        diags.append(f"Using pytest.ini: {pytest_ini.name}")
        testpaths, python_files, norecursedirs, config_source = _parse_pytest_ini(pytest_ini, cfg)
    elif pyproject_toml:
        diags.append(f"Using pyproject.toml: {pyproject_toml.name}")
        testpaths, python_files, norecursedirs, config_source = _parse_pyproject_toml(pyproject_toml, cfg)
    else:
        # Effective defaults
        default_base = ["tests"] if (root / "tests").exists() else ["."]
        testpaths, python_files, norecursedirs, config_source = (
            default_base,
            list(cfg.default_python_files),
            list(cfg.norecursedirs),
            "default",
        )
        diags.append(f"No pytest config; using defaults: testpaths={testpaths}, python_files={python_files}")

    if not python_files: python_files = list(cfg.default_python_files)  
    if not norecursedirs: norecursedirs = list(cfg.norecursedirs)

    
    bases = [ (root / p).resolve() for p in testpaths if (root / p).exists() ]

    if not bases:
        bases = [root.resolve()]

    missing = [p for p in testpaths if not (root / p).exists()]
    for p in missing:
        diags.append(f"Configured testpath does not exist: {p}")
    if not any((root / p).exists() for p in testpaths):
        diags.append("All configured testpaths missing; scanning from repo root")
        testpaths = ["."]

    

    MAX_SCAN = getattr(cfg, "max_files_scanned", 1000)
    scanned_files = 0
    stop = False
    for base in bases:
        for dirpath, dirnames, filenames in os.walk(base):

            if stop:
                break

            depth = Path(dirpath).relative_to(base).parts
            if len(depth) > cfg.max_walk_depth:
                dirnames[:] = []
                continue
            
            # prune dotdirs and norecursedirs
            dirnames[:] = [d for d in dirnames if not _skip_dir(d, norecursedirs)]
            for name in filenames:
                if stop:
                    break
                scanned_files += 1
                if scanned_files > MAX_SCAN:
                    diags.append(f"Visited {scanned_files} files; exceeded max_files_scanned limit of {MAX_SCAN}")
                    stop = True
                    break
                if any(fnmatch.fnmatch(name, pat) for pat in python_files):
                    full = Path(dirpath) / name
                    rel = (full).relative_to(root).as_posix()
                    test_files.append(rel)
                    

    # Deduplicate and sort for stability
    test_files = sorted(set(test_files))
    warnings: list[str] = []
    if not test_files:
        warnings.append("No test files matched the effective patterns under the selected testpaths. Examples of effective patterns: test_*.py, *_test.py")

    normalized_paths = ["." if (p == "" or p == str(root)) else p for p in testpaths]
    diags.append(f"Using {config_source}; testpaths={normalized_paths}, python_files={python_files}, norecursedirs={norecursedirs[:5]}, test_files={test_files[:5]}")
    return (
        TestsInfo(
            paths=normalized_paths,    # keep as provided (relative strings)
            files=test_files,                     # concrete, repo-relative files
            patterns=list(python_files),          # the globs used
            config_source=config_source,
            warnings=warnings,
        ),
        diags,
    )

                
        
    
    



