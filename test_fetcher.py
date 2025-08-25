import asyncio
from src.gitinside.fetcher.github import GithubFetcher
from pathlib import Path

async def main():
    fetcher = GithubFetcher()

    owner = "sanjayc0204"
    repo = "git_test"

    try:
        print(f"Fetching {owner}/{repo}")
        repo_path = fetcher.fetch(owner=owner, repo=repo)

        print(f"Repository downloaded to: {repo_path}")
        print("\nTop-Level files/directories:")
        for item in repo_path.iterdir():
            print(f"- {item.name}")
    
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("\nDone! Temporary files will be cleaned up automatically")

if __name__ == "__main__":
    asyncio.run(main())