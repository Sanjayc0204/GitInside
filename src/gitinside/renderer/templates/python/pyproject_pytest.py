from ....detect.plan import Plan

print("rendering pyproject plan")
def render(plan: Plan) -> str:
    base_image = f"python:{plan.python_tag}"

    lines = [
        f"FROM {base_image}",
        "ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1",
        "ENV PYTHONPATH=/app"
        "WORKDIR /app",
        "COPY . .",
        "RUN python -m pip install -U pip && \\",
        "python -m pip install . && \\",
        "python -m pip install --no-cache-dir pytest pytest-json-report",
        'ENTRYPOINT ["python","/app/shim.py"]',
    ]
    return "\n".join(lines) + "\n"
