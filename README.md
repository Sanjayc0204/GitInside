# GitInside v0.1

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

GitInside is a powerful tool for running tests in isolated Docker containers by automatically detecting and configuring the required environment based on project configuration files.

## 🚀 Current Features (v0.1)

- **Automatic Configuration Detection**
  - Detects and parses configuration files like `requirements.txt`, `pyproject.toml`, etc.
  - Supports Python projects with pytest
  - Automatically resolves and installs project dependencies

- **Docker-based Isolation**
  - Runs tests in isolated Docker containers
  - Clean environment for each test run
  - Automatic container cleanup after execution

- **Test Execution**
  - Runs tests with appropriate test runners
  - Captures and displays test output
  - Collects test results and coverage reports

## 📦 Prerequisites

- Python 3.8+
- Docker Engine
- Git

## 🛠 Installation

```bash
# Clone the repository
git clone https://github.com/Sanjayc0204/GitInside.git
cd GitInside

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

## 🚀 Usage

Run tests for a GitHub repository:

```bash
python -m gitinside.main --owner <owner> --repo <repository>
```

Example:
```bash
python -m gitinside.main --owner Sanjayc0204 --repo gitinside-happy-test
```

## 🚧 Roadmap

### v0.2 (Next Release)
- Deploy test environments on Google Cloud Platform (GCP)
- Support for more configuration file types
- Enhanced error handling and logging

### Future Versions
- Run containerized servers
- Full-stack application testing
- Support for additional programming languages
- CI/CD integration

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.