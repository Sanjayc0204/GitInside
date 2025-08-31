
from gitinside.detect.plan import Plan
from gitinside.renderer.templates.python.pyproject_pytest import render as pyproject_pytest_render
from gitinside.renderer.templates.python.requirements_pytest import render as requirements_pytest_render

# For posterity in case we use aliases later
def pick_template(plan: Plan):
    return plan.kind

def render_dockerfile(plan: Plan):
    tmp = pick_template(plan)
    match tmp:
        case "python-pyproject-pytest":
            pyproject_pytest_render(plan)
        case "python-requirements-pytest":
            requirements_pytest_render(plan)

