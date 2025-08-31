import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open
from gitinside.detect.python.tests import detect_tests, _find_pytest, _find_pyproject_toml
from gitinside.detect.config import DetectorConfig
from gitinside.detect.plan import TestsInfo

@pytest.fixture
def temp_dir():
    with pytest.MonkeyPatch.context() as mp:
        with tempfile.TemporaryDirectory() as td:
            temp_path = Path(td)
            (temp_path / "test_file.py").touch()
            (temp_path / "test_dir").mkdir()
            (temp_path / "test_dir" / "test_file2.py").touch()
            (temp_path / "test_dir" / "not_a_test.txt").touch()
            (temp_path / "venv").mkdir()
            (temp_path / ".git").mkdir()
            yield temp_path

def test_find_pytest(temp_dir):
    # Test when pytest.ini doesn't exist
    assert _find_pytest(temp_dir) is None
    
    # Create pytest.ini
    (temp_dir / "pytest.ini").touch()
    assert _find_pytest(temp_dir) == temp_dir / "pytest.ini"

def test_find_pyproject_toml(temp_dir):
    # Test when pyproject.toml doesn't exist
    assert _find_pyproject_toml(temp_dir) is None
    
    # Create pyproject.toml
    (temp_dir / "pyproject.toml").touch()
    assert _find_pyproject_toml(temp_dir) == temp_dir / "pyproject.toml"

def test_detect_tests_with_pytest_ini(temp_dir):
    # Create pytest.ini with custom configuration
    pytest_ini = """
    [pytest]
    testpaths = test_dir
    python_files = test_*.py
    norecursedirs = .git venv
    """
    (temp_dir / "pytest.ini").write_text(pytest_ini)
    
    config = DetectorConfig()
    tests_info, diags = detect_tests(temp_dir, config)
    
    assert isinstance(tests_info, TestsInfo)
    assert "pytest.ini" in diags[0]
    assert "test_dir/test_file2.py" in tests_info.files
    assert "test_file.py" not in tests_info.files  # Not in test_dir

def test_detect_tests_with_pyproject_toml(temp_dir):
    # Create pyproject.toml with pytest configuration
    pyproject_toml = """
    [tool.pytest.ini_options]
    testpaths = ["test_dir"]
    python_files = "test_*.py"
    norecursedirs = [".git", "venv"]
    """
    (temp_dir / "pyproject.toml").write_text(pyproject_toml)
    
    config = DetectorConfig()
    tests_info, diags = detect_tests(temp_dir, config)
    
    assert isinstance(tests_info, TestsInfo)
    assert "pyproject.toml" in diags[0]
    assert "test_dir/test_file2.py" in tests_info.files
    assert "test_file.py" not in tests_info.files

def test_detect_tests_default_config(temp_dir):
    # Test with no config files (should use defaults)
    (temp_dir / "tests").mkdir()
    (temp_dir / "tests" / "test_default.py").touch()
    
    config = DetectorConfig()
    tests_info, diags = detect_tests(temp_dir, config)
    
    assert "No pytest config" in diags[0]
    assert "tests/test_default.py" in tests_info.files

def test_detect_tests_nonexistent_testpath(temp_dir):
    # Test with non-existent testpath
    pytest_ini = """
    [pytest]
    testpaths = non_existent_dir
    """
    (temp_dir / "pytest.ini").write_text(pytest_ini)
    
    config = DetectorConfig()
    tests_info, diags = detect_tests(temp_dir, config)
    
    assert "Configured testpath does not exist: non_existent_dir" in diags
    # Should fall back to scanning from root
    assert any(f.endswith("test_file.py") for f in tests_info.files)