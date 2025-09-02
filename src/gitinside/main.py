import tempfile
from .runner import Runner


def main():
    print("Running runner...")
    runner = Runner()
    runner.run(owner="Sanjayc0204", repo="gitinside-happy-test")

if __name__ == "__main__":
    main()