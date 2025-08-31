

import os
import subprocess
import sys


def main():
    results_dir = "/results"
    os.makedirs(results_dir, exist_ok=True)

    proc = subprocess.run(
        ["pytest", ".", "--junitxml=/results/report.xml",
         "--json-report", "--json-report-file=/results/report.json"]
    )

    sys.exit(proc.returncode)

if __name__ == "__main__":
    main()