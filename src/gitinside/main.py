import argparse
import sys
from typing import Optional
from pathlib import Path

from .runner import Runner


def parse_args():
    parser = argparse.ArgumentParser(
        description="GitInside - Run tests in isolated Docker containers"
    )
    parser.add_argument(
        "--owner",
        required=True,
        help="GitHub repository owner (username or organization)",
    )
    parser.add_argument(
        "--repo",
        required=True,
        help="GitHub repository name",
    )
    parser.add_argument(
        "--token",
        help="GitHub access token (optional, for private repositories)",
    )
    parser.add_argument(
        "--ref",
        default="main",
        help="Git reference (branch, tag, or commit hash), defaults to 'main'"
    )
    parser.add_argument(
        "--profile",
        default="default",
        help="Profile name from gitinside-config.yaml/.gitinsiderc.yaml (default: default)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path.cwd() / ".gitinside" / "results",
        help="Directory to store test results (default: .gitinside/results/)",
    )
    return parser.parse_args()


def main() -> int:
    try:
        args = parse_args()
        
        print(f"Running tests for {args.owner}/{args.repo}...")
        
        runner = Runner()
        runner.run(
            owner=args.owner,
            repo=args.repo,
            token=args.token,
            ref=args.ref,
            profile=args.profile,
        )
        
        print("\nTest execution completed successfully!")
        return 0
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())