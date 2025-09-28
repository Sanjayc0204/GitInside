import argparse
import sys
from typing import Optional
from pathlib import Path

from .runner import Runner


def parse_github_url(url: str) -> tuple[str, str]:
    """Parse GitHub URL into (owner, repo) tuple.
    
    Args:
        url: GitHub repository URL or owner/repo string
        
    Returns:
        Tuple of (owner, repo)
        
    Raises:
        ValueError: If URL cannot be parsed
    """
    if not url or url == "default":
        raise ValueError("No URL provided")
        
    # Handle owner/repo format
    if '/' in url and '://' not in url and ' ' not in url:
        parts = url.split('/')
        if len(parts) == 2:
            return parts[0], parts[1].replace('.git', '')
    
    # Handle full URLs
    url = url.replace('https://', '').replace('http://', '').rstrip('/')
    if url.endswith('.git'):
        url = url[:-4]
    
    parts = url.split('/')
    if 'github.com' in parts:
        # Format: github.com/owner/repo
        idx = parts.index('github.com')
        if len(parts) < idx + 3:
            raise ValueError("Invalid GitHub URL format")
        return parts[idx + 1], parts[idx + 2]
    elif len(parts) >= 2:
        # Format: owner/repo (from URL without domain)
        return parts[-2], parts[-1].replace('.git', '')
    
    raise ValueError("Could not parse GitHub URL")


def parse_args():
    parser = argparse.ArgumentParser(
        description="GitInside - Run tests in isolated Docker containers"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--url",
        help="GitHub repository URL (e.g., https://github.com/owner/repo or owner/repo)",
    )
    group.add_argument(
        "--owner",
        help="GitHub repository owner (username or organization)",
    )
    parser.add_argument(
        "--repo",
        help="GitHub repository name (required if --owner is used)",
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
        
        try:
            if args.url:
                owner, repo = parse_github_url(args.url)
            else:
                if not args.owner or not args.repo:
                    raise ValueError("Both --owner and --repo are required when not using --url")
                owner, repo = args.owner, args.repo
            
            print(f"Running tests for {owner}/{repo}...")
            
            runner = Runner()
            runner.run(
                owner=owner,
                repo=repo,
                token=args.token,
                ref=args.ref,
                profile=args.profile,
            )
            return 0
            
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        
        
        print("\nTest execution completed successfully!")
        return 0
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())