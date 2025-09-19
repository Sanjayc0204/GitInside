from typing import Optional
from pathlib import Path
from .base import BaseFetcher
import os, tarfile, tempfile, requests, shutil

"""
1. You can make temp files using tempfile
2. The github tarball api gives a redirect link. Python requests allows redirects by default
2.a You can stream the contents of the tar link into a certain path by using shutil and downloading it in 1MB chunks
3. You need to be vary of "zip-slip" by malicious repos by making sure every file and directory in the tar has a valid directory name that starts with the destination folder
4. Symlinks can also be malicious
5. Github tarballs have a top-level wrapper folder. You can flatten it by bringing its contents up to the build folder and deletingn the wrapper folder
"""

class GithubFetcher(BaseFetcher):
    def __init__(self, token: Optional[str] = None):
        self.token = token

    @staticmethod
    def safe_extract(tf: tarfile.TarFile, dest: str) -> None:
        """Extract safely (prevent path traversal)."""
        root = os.path.realpath(dest)
        for m in tf.getmembers():
            target = os.path.realpath(os.path.join(dest, m.name))
            if not (target == root or target.startswith(root + os.sep)):
                raise RuntimeError(f"Unsafe path in tar: {m.name}")
            if m.issym() or m.islnk():
                raise RuntimeError(f"Symlink not allowed in tar: {m.name}")
        tf.extractall(dest)

    def fetch(self, owner: str, repo: str, ref: Optional[str] = "main") -> Path:
        # 1) unique workspace under /tmp
        build_dir = Path(tempfile.mkdtemp(prefix=f"build-{owner}-{repo}-"))

        url = f"https://api.github.com/repos/{owner}/{repo}/tarball/{ref}"
        headers = {"Accept": "application/vnd.github+json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        # 2) stream tarball to disk
        tar_path = build_dir / "repo.tar.gz"
        with requests.get(url, headers=headers, stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(tar_path, "wb") as f:
                shutil.copyfileobj(r.raw, f, length=1024 * 1024)  # 1 MB chunks

        # 3) safe extract, then delete archive
        with tarfile.open(tar_path, "r:gz") as tf:
            self.safe_extract(tf, str(build_dir))
        try:
            tar_path.unlink()
        except FileNotFoundError:
            pass

        # 4) flatten single top-level wrapper dir (GitHub tarballs)
        top_dirs = [p for p in build_dir.iterdir() if p.is_dir()]
        if len(top_dirs) == 1:
            extracted_root = top_dirs[0]
            for p in extracted_root.iterdir():
                p.rename(build_dir / p.name)
            extracted_root.rmdir()

        # 5) write a default .dockerignore
        (build_dir / ".dockerignore").write_text(
            ".git\n.env\n**/.env\n**/.aws\n**/.ssh\nid_*\n__pycache__\n*.ipynb_checkpoints\nnode_modules\n.DS_Store\n",
            encoding="utf-8",
        )

        return build_dir
