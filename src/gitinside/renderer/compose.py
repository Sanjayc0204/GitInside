
import shutil
from pathlib import Path
from ..detect.plan import Plan
from .templates.python.pyproject_pytest import render as pyproject_pytest_render
from .templates.python.requirements_pytest import render as requirements_pytest_render

# For posterity in case we use aliases later
def pick_template(plan: Plan):
    return plan.deps.kind

def write_dockerfile(content: str, directory: Path):
    dockerfile_path = directory / "Dockerfile"
    dockerfile_path.write_text(content, encoding = "utf-8")
    return dockerfile_path

def copy_file(source: Path, destination_dir: Path):
    if not source.is_file():
        raise FileNotFoundError(f"Source file not found: {source}")
    if not destination_dir.is_dir():
        raise FileNotFoundError(f"Destination directory not found: {destination_dir}")
    
    destination_path = destination_dir / source.name
    shutil.copy2(source, destination_path)
    return destination_path

def render_dockerfile(plan: Plan, root: Path):
    # Ensure root is a Path object if it isn't already
    root = Path(root)
    
    # Get the directory where this file is located
    current_dir = Path(__file__).parent
    
    # Construct path to shim (assuming it's in a 'shim' directory next to this file)
    shim_source = current_dir / "templates" / "python" / "shim" / "shim.py"
    
    tmp = pick_template(plan)
    print("tmp = ", tmp)
    match tmp:
        case "python-pyproject-pytest":
            docker_contents = pyproject_pytest_render(plan)
            write_dockerfile(docker_contents, root)
            copy_file(shim_source, root)
            for path in root.iterdir():
                print(path, "\n")
        case "python-requirements-pytest":
            docker_contents = requirements_pytest_render(plan)
            write_dockerfile(docker_contents, root)
            copy_file(shim_source, root)
            for path in root.iterdir():
                print(path, "\n")

