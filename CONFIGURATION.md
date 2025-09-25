# GitInside Configuration Guide

This document explains how to configure your repository to work with GitInside using the `.gitinsiderc.yaml` configuration file.

## Configuration File Location

Place the `.gitinsiderc.yaml` file in the root of your repository, alongside the `src` and `env` directories.

## Configuration Structure

The configuration file supports the following structure:

```yaml
version: 1  # Configuration version
profiles:
  profile_name:  # Can be anything (e.g., 'test', 'build', 'run')
    description: "Description of what this profile does"
    working_dir: "."  # Base working directory
    environment:  # Environment variables
      KEY: "value"
    pre_execute:  # Commands to run before main execution
      - command: "command to run"
        cwd: "working/directory"  # Optional
    execute:  # Main command to execute
      command: "main command"
      args: ["arg1", "arg2"]  # Optional arguments
      cwd: "working/directory"  # Optional
      timeout: 300  # Optional timeout in seconds
    post_execute:  # Commands to run after main execution
      - command: "cleanup command"
    artifacts:  # Files to collect after execution
      - path: "path/to/files/**/*"  # Supports glob patterns
        target: "/results/destination"  # Where to copy in the container
```

## Example Configurations

### Simple Python Script

```yaml
version: 1
profiles:
  run:
    description: "Run the main Python script"
    environment:
      PYTHONPATH: "${PWD}/src"
    pre_execute:
      - command: "pip install -r requirements.txt"
    execute:
      command: "python"
      args: ["main.py", "--input", "data/input.txt"]
    artifacts:
      - path: "output/**/*"
        target: "/results"
```

### Test Suite

```yaml
version: 1
profiles:
  test:
    description: "Run tests"
    environment:
      PYTHONPATH: "${PWD}/tests:${PWD}/src"
    pre_execute:
      - command: "pip install -r requirements-dev.txt"
    execute:
      command: "pytest"
      args: ["-v", "--cov=src", "--junitxml=/results/test-results.xml"]
    artifacts:
      - path: "test-results.xml"
        target: "/results"
      - path: ".coverage"
        target: "/results"
```

### Build and Package

```yaml
version: 1
profiles:
  build:
    description: "Build and package the application"
    pre_execute:
      - command: "pip install build"
    execute:
      command: "python"
      args: ["-m", "build", "--outdir", "dist"]
    artifacts:
      - path: "dist/*"
        target: "/results/dist"
```

## Using Profiles

When running GitInside, you can specify which profile to use. If no profile is specified, the `default` profile will be used.

### Example: Using a Specific Profile

```bash
# Using the 'test' profile
gitinside run --profile test

# Using the default profile (same as not specifying)
gitinside run
```

## Environment Variables

You can use environment variables in your configuration using the `${VAR}` syntax. The following variables are available:

- `PWD`: The root directory of the repository
- `HOME`: The user's home directory
- Any environment variables set in the `environment` section

## Artifact Collection

The `artifacts` section specifies which files should be collected after execution. You can use glob patterns to match multiple files:

- `*.txt` - Matches all .txt files in the current directory
- `**/*.log` - Matches all .log files in all subdirectories
- `results/**/*` - Matches all files in the results directory and its subdirectories

## Timeouts

You can specify a timeout for the main execution in seconds. If the command runs longer than this, it will be terminated.

## Best Practices

1. **Keep it Simple**: Start with a minimal configuration and add complexity as needed.
2. **Use Profiles**: Create separate profiles for different tasks (test, build, run, etc.).
3. **Document**: Use the `description` field to explain what each profile does.
4. **Test Locally**: Test your configuration locally before committing it.
5. **Version Control**: Commit your `.gitinsiderc.yaml` file to version control.
