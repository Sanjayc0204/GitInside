"""
Input (Repo URL)
- Fetcher (Clone repo)
- Detector (Analyze -> plan)
- Renderer (Plan -> Output)
- Final Result
"""

from ntpath import exists
from operator import truediv
from tkinter import N
from gitinside.detect.compose import compose_plan
from gitinside.detect.config import DetectorConfig
from gitinside.detect.python.deps import detect_deps
from gitinside.detect.python.tests import detect_tests
from gitinside.fetcher.github import GithubFetcher
from gitinside.renderer.compose import render_dockerfile
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
        image:str,
        command: Optional[str]= None,
        volumes: Optional[Dict[str, Dict[str, str]]] = None,
        environment: Optional[Dict[str, str]] = None,
        detach: bool = False,
        remove: bool = True,
        **kwargs):
        client = docker.from_env()

        try:
            container = client.containers.run(
                image=image,
                command=command,
                volumes=volumes,
                environment=environment,
                detach=detach,
                remove=remove,
                **kwargs
            )
            if detach:
                return container.id
            else:
                return container.decode('utf-8') if container else ""
        except docker.errors.APIError as e:
            print(f"Failed to run container: {e}")
        raise


    
    def run(self, token: Optional[str], owner: str, repo: str, ref:Optional[str]):
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
        
        if not _is_docker_running():
            print("Docker daemon not running. Try again with the daemon running.", file=sys.stderr)
            sys.exit(1)
        
        
        try:
            # 1. Fetch Github repo
            self.temp_dir = fetcher.fetch(owner, repo, ref)

            # 2. Detect project type and requirements
            deps_info = detect_deps(self.temp_dir, cfg=DetectorConfig())
            tests_info = detect_tests(self.temp_dir, cfg=DetectorConfig())
            plan = compose_plan(self.temp_dir, deps_info, tests_info)

            # 3. Generate dockerfile
            render_dockerfile(plan, self.temp_dir)

            # 4. Build docker image
            image_id = _docker_build(self.temp_dir, f"{owner}+{repo}:{ref}")

            with tempfile.TemporaryDirectory() as temp_dir:
                volumes = {
                    os.path.abspath(temp_dir): {
                        'bind': '/results',
                        'mode': 'rw'
                    }
                }
                environment = {
                    "PYTHONUNBUFFERED": "1",
                    "OUTPUT_DIR": "/results"
                }

                # Run container and capture output
                logs = self._run_container(
                    image=image_id,
                    volumes=volumes,
                    environment=environment
                )
                print(logs)

                results_dir = Path(temp_dir)
                report_files = list(results_dir.glob("*.xml")) + list(results_dir.glob("*.json"))
                
                if not report_files:
                    print("No report files found in container output")
                else:
                    print(f"Found {len(report_files)} report files")
                    for report in report_files:
                        print(f"- {report.name}")


        except Exception as e:
            print(f"Error: {e}")
            raise

