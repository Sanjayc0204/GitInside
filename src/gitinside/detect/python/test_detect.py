import os
import sys
import tempfile
from pathlib import Path
import pytest

# Add the src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Import from the current package
from gitinside.detect.plan import DepsInfo
from gitinside.detect.python.deps import detect_deps, _get_python_version_from_pyproject_toml
from gitinside.detect.config import DetectorConfig  # Updated import path

@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as td:
        yield Path(td)
    
def test_detect_deps_with_pyproject_toml(temp_dir: Path):
    pyproject_content = """
    [project]
    name = "test_project"
    version = "0.1.0"
    requires-python = ">=3.9"
    """
    (temp_dir / "pyproject.toml").write_text(pyproject_content)
    
    config = DetectorConfig(default_python="3.9")
    deps_info, diags = detect_deps(temp_dir, config)
    
    assert deps_info.kind == "pyproject"
    assert deps_info.path == "pyproject.toml"
    assert deps_info.python == ">=3.9"  # Should match the version in pyproject_content

def test_detect_deps_with_requirements_file(temp_dir: Path):
    (temp_dir / "requirements.txt").write_text("requiests==2.28.1\npytest==7.2.0")

    config = DetectorConfig(default_python="3.9")
    deps_info, diags = detect_deps(temp_dir, config)
    
    assert deps_info.kind == "requirements"
    assert deps_info.path == "requirements.txt"
    assert deps_info.python == "3.9"

def test_detect_deps_no_files(temp_dir: Path):
    config = DetectorConfig(default_python="3.9")
    deps_info, diags = detect_deps(temp_dir, config)
    
    assert deps_info.kind == "requirements"
    assert deps_info.path == "requirements.txt"
    assert deps_info.python == "3.9"

def test_get_python_version_from_pyproject_toml(temp_dir: Path):
    # Test with standard project config
    pyproject_content = """
    [project]
    name = "test_project"
    version = "0.1.0"
    requires-python = ">=3.9"
    """
    (temp_dir / "pyproject.toml").write_text(pyproject_content)
    version = _get_python_version_from_pyproject_toml(temp_dir / "pyproject.toml")
    assert version == ">=3.9"
    
    # Test with poetry config
    content = """
    [tool.poetry]
    name = "test"
    version = "0.1.0"
    
    [tool.poetry.dependencies]
    python = "^3.8"
    """
    (temp_dir / "pyproject.toml").write_text(content)
    version = _get_python_version_from_pyproject_toml(temp_dir / "pyproject.toml")
    assert version == "^3.8"

    # Test with no python version
    pyproject_content = """
    [project]
    name = "test"
    version = "0.1.0"
    """
    (temp_dir / "pyproject.toml").write_text(pyproject_content)
    version = _get_python_version_from_pyproject_toml(temp_dir / "pyproject.toml")
    assert version is None

