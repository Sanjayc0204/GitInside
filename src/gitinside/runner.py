"""
Input (Repo URL)
- Fetcher (Clone repo)
- Detector (Analyze -> plan)
- Renderer (Plan -> Output)
- Final Result
"""

from ntpath import exists
from operator import truediv
import os
from pathlib import Path
from tkinter import N
from typing import Optional, Dict

from docker.errors import APIError
from .detect.compose import compose_plan
from .detect.config import DetectorConfig
from .detect.python.deps import detect_deps
from .detect.python.tests import detect_tests
from .fetcher.github import GithubFetcher
from .renderer.compose import render_dockerfile
import docker
import sys


class Runner:
    def __init__(self, output_dir: str = "output", cleanup: bool = True):
        output_dir = Path(output_dir)
        cleanup = cleanup
        temp_dir: Optional[Path] = None
    
    def _is_docker_running(self):
        try:
            client = docker.from_env()
            client.ping()
            return True
        except:
            return False
    
    def _docker_build(
        self,
        path: str,
        tag: str = "gitinside:latest",
        dockerfile: str = "Dockerfile",
        build_args: Optional[Dict[str, str]] = None):
        client = docker.from_env()

        try:
            image, logs = client.images.build(
                path=path,
                tag=tag,
                dockerfile=dockerfile,
                buildargs=build_args,
                rm=True,
                forcerm=True
            )
            return image.id
        except docker.errors.BuildError as e:
            print(f"Build failed: {e}")
            for line in e.build_log:
                if 'stream' in line:
                    print(line['stream'].strip())
            raise
        except Exception as e:
            print(f"Error building image: {e}")
            raise
    
    def _run_container(
        self,
        image: str,
        command: Optional[str] = None,
        volumes: Optional[Dict[str, Dict[str, str]]] = None,
        environment: Optional[Dict[str, str]] = None,
        timeout: int = None,
        detach: bool = False,
        remove: bool = True,
        **kwargs):
        client = docker.from_env()
        container = None

        try:
            container = client.containers.create(
                image=image,
            volumes=volumes or {},
            environment=environment or {},
            detach=True,
            )

            container.start()

            result = container.wait(timeout=timeout)

            exit_code = result.get("StatusCode", 1 if isinstance(result, int) else 1)

            # 4) Get combined logs (stdout + stderr)
            logs = container.logs(stdout=True, stderr=True)
            logs_text = logs.decode("utf-8", errors="replace")

            return exit_code, logs_text
        except APIError as e:
            raise
        finally:
            if container is not None:
                try:
                    container.remove(force=True)
                except Exception:
                    pass
    
    def run(self, owner: str, repo: str, token: Optional[str] = None, ref:Optional[str] = "main"):
        """
        Main execution flow:
        1. Fetch repository
        2. Detect project type and requirements
        3. Generate dockerfile
        4. Build image
        5. Run image
        6. Clean up if needed
        """
        fetcher = GithubFetcher()
        if token:
            fetcher = GithubFetcher(token=token)
        
        if not self._is_docker_running():
            print("Docker daemon not running. Try again with the daemon running.", file=sys.stderr)
            sys.exit(1)
        
        
        try:
            print("Fetching repo...")
            # 1. Fetch Github repo
            self.temp_dir = fetcher.fetch(owner, repo, ref)
            print("Fetched!")

            # 2. Detect project type and requirements
            print("Detecting dependencies...")
            deps_info, diags = detect_deps(self.temp_dir, cfg=DetectorConfig())
            print('\n'.join(map(str, diags)))
            tests_info, diags = detect_tests(self.temp_dir, cfg=DetectorConfig())
            print('\n'.join(map(str, diags)))
            plan = compose_plan(self.temp_dir, deps_info, tests_info)
            print("Detected!")

            # 3. Generate dockerfile
            print("Generating dockerfile...")
            render_dockerfile(plan, self.temp_dir)
            print("Generated!")

            # 4. Build docker image
            print("Building docker image...")
            image_id = self._docker_build(str(self.temp_dir), f"{owner}-{repo}:{ref}".lower())
            print("Docker image built!")

            # 5. Run docker image
            print("Running docker image...")
            print("Running docker image...")

            base = Path.cwd()
            host_results = base / ".gitinside" / "results" / f"{owner}.{repo}"
            host_results.mkdir(parents=True, exist_ok=True)

            volumes = {
                str(host_results.resolve()): {"bind": "/results", "mode": "rw"}
            }
            environment = {
                "PYTHONUNBUFFERED": "1",
                "PYTHONPATH": "/app",
                "OUTPUT_DIR": "/results"
            }

            logs = self._run_container(
                image=image_id,
                volumes=volumes,
                environment=environment
            )
            print(logs)

            results_dir = host_results
            report_files = list(results_dir.rglob("*.xml")) + list(results_dir.rglob("*.json"))

            if not report_files:
                print(f"No report files found in {results_dir}")
            else:
                print(f"Found {len(report_files)} report files")
                for report in report_files:
                    print(f"- {report.relative_to(results_dir)}")

            print("Finished running!")



        except Exception as e:
            print(f"Error: {e}")
            raise
