from pathlib import Path
from typing import Literal
import json, hashlib

from gitinside.detect.plan import DepsInfo, Plan, TestsInfo


def _stable_hash(d: dict) -> str:
    blob = json.dumps(d, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def compose_plan(
    root: Path,
    deps: DepsInfo,
    tests: TestsInfo,
    default_python_tag: str = "3.12-slim",
    default_pytest_args: list[str] | None = None,
    network_policy: Literal["pypi-only", "none", "full"] = "pypi-only",
    env_allow: list[str] | None = None,
    apt_allow: list[str] | None = None,
) -> Plan:
    # Initialize mutable defaults
    default_pytest_args = default_pytest_args or ["-q", "--maxfail=5", "--disable-warnings", "--durations=10"]
    python_tag = default_python_tag
    diagnostics: list[str] = getattr(deps, "diagnostics", []) or []

    if deps.python and deps.python.strip():
        bounds = [b.strip() for b in deps.python.split(",") if b.strip()]
        try:
            # First look for exact version specifiers (== or =)
            for bound in bounds:
                if "==" in bound:
                    version = bound.split("==", 1)[1].strip()
                    python_tag = f"{version}-slim"
                    break
                elif "=" in bound and not bound.startswith((">", "<")):
                    version = bound.split("=", 1)[1].strip()
                    python_tag = f"{version}-slim"
                    break
            else:
                # No exact version found, look for lower bounds (>=)
                for bound in bounds:
                    if ">=" in bound:
                        version = bound.split(">=", 1)[1].strip()
                        python_tag = f"{version}-slim"
                        break
                else:
                    # No lower bound, check for simple version number
                    for bound in bounds:
                        if bound[0].isdigit():
                            version = bound.split(None, 1)[0].strip()
                            python_tag = f"{version}-slim"
                            break
                    else:
                        diagnostics.append(f"Could not parse Python version from: {deps.python}")
        except (IndexError, ValueError) as e:
            diagnostics.append(f"Invalid Python version specifier: {deps.python} - {str(e)}")
            python_tag = default_python_tag

    if deps.kind == "pyproject":
        dockerfile_template = "python-pyproject-pytest"
    elif deps.kind == "requirements":
        dockerfile_template = "python-requirements-pytest"
    else:
        dockerfile_template = "python-requirements-pytest"
        diagnostics.append(
            f"Unsupported project type '{deps.kind}'. Expected 'requirements' or 'pyproject'."
        )

    tests_mode = "discovery"
    runner = "pytest"
    env_allow = env_allow or []
    apt_allow = apt_allow or []
    pytest_args = default_pytest_args
    artifacts = {"json": "/results/report.json", "junit": "/results/junit.xml"}
    limits = {"timeout_sec": 300, "max_fail": 5, "max_files_scanned": 1000}
    work_dir = "."

    # Add test diagnostics
    diagnostics.extend(getattr(tests, "diagnostics", []) or [])

    # Normalize paths
    deps_path_norm = Path(deps.path).as_posix() if deps.path else ""
    test_paths_norm = [Path(p).as_posix() for p in (tests.paths or [])]
    test_patterns_sorted = sorted(tests.patterns or [])
    env_allow_sorted = sorted(env_allow)
    apt_allow_sorted = sorted(apt_allow)

    # Build hash material
    material = {
        "runner": runner,
        "dockerfile_template": dockerfile_template,
        "python_tag": python_tag,
        "deps": {
            "kind": deps.kind,
            "path": deps_path_norm,
            "python": deps.python or "",
            "constraints": deps.constraints or "",
            "extra_index_url": deps.extra_index_url or "",
        },
        "tests": {
            "paths": test_paths_norm,
            "patterns": test_patterns_sorted,
            "mode": tests_mode,
        },
        "limits": limits,
        "network_policy": network_policy,
        "work_dir": work_dir,
        "pytest_args": pytest_args,
        "env_allow": env_allow_sorted,
        "apt": apt_allow_sorted,
    }
    plan_hash = _stable_hash(material)

    return Plan(
        runner=runner,
        deps=deps,
        tests=tests,
        env_allowed=env_allow_sorted,
        python_tag=python_tag,
        work_dir=work_dir,
        dockerfile_template=dockerfile_template,
        artifacts=artifacts,
        limits=limits,
        network_policy=network_policy,
        tests_mode=tests_mode,
        apt=apt_allow_sorted,
        pytest_args=" ".join(pytest_args),
        diagnostics=diagnostics,
        schema_version=1,
        plan_hash=plan_hash,
    )