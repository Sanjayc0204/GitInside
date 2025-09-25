"""
Shim Generator for GitInside

This module handles the generation of shim scripts based on the .gitinsiderc.yaml configuration.
"""

import os
import shutil
import subprocess
import sys
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


def load_config(config_path: str = ".gitinsiderc.yaml") -> Dict[str, Any]:
    """Load the GitInside configuration file."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            # Validate config structure
            if 'version' not in config or 'profiles' not in config:
                raise ValueError("Invalid configuration: missing required fields")
            return config
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file {config_path} not found")


def generate_shim_script(config: Dict[str, Any], profile: str = "default") -> str:
    """Generate a shim script based on the configuration and profile."""
    if profile not in config['profiles']:
        raise ValueError(f"Profile '{profile}' not found in configuration")
    
    profile_config = config['profiles'][profile]
    
    # Start building the shim script
    lines = [
        '#!/usr/bin/env python3',
        'import os',
        'import shutil',
        'import subprocess',
        'import sys',
        'from pathlib import Path',
        'import json',
        'import time',
        'import glob',
        'import signal',
        'from typing import List, Dict, Any, Optional\n',
        'class TimeoutError(Exception):',
        '    pass\n',
        'def run_command(cmd: List[str], cwd: str = "", env: Optional[Dict[str, str]] = None, timeout: int = 300) -> int:',
        '    """Run a command with timeout and environment variables."""',
        '    if not cmd:',
        '        return 0',
        ''    
        '    # Set up environment',
        '    cmd_env = os.environ.copy()',
        '    if env:',
        '        cmd_env.update(env)\n',
        '    # Set up working directory',
        '    cmd_cwd = Path(cwd).resolve() if cwd else Path.cwd()',
        '    cmd_cwd.mkdir(parents=True, exist_ok=True)\n',
        '    print("Executing: {} in {}".format(" ".join(cmd), cmd_cwd))\n',
        '    try:',
        '        process = subprocess.Popen(',
        '            cmd,',
        '            cwd=cmd_cwd,',
        '            env=cmd_env,',
        '            stdout=subprocess.PIPE,',
        '            stderr=subprocess.STDOUT,',
        '            universal_newlines=True,',
        '            bufsize=1',
        '        )\n',
        '        # Read output in real-time',
        '        while True:',
        '            output = process.stdout.readline()',
        '            if output == "" and process.poll() is not None:',
        '                break',
        '            if output:',
        '                print(output.strip())\n',
        '        return process.returncode',
        '    except subprocess.TimeoutExpired:',
        '        process.kill()',
        '        raise TimeoutError(f"Command timed out after {timeout} seconds")',
        '    except Exception as e:',
        '        print(f"Error executing command: {e}", file=sys.stderr)',
        '        return 1\n',
        'def collect_artifacts(artifacts: List[Dict[str, str]]) -> None:',
        '    """Collect artifacts after execution."""\n',
        '    results_dir = Path("/results")\n',
        '    results_dir.mkdir(exist_ok=True, parents=True)\n',
        '    for artifact in artifacts:',
        '        src_pattern = artifact["path"]',
        '        target_dir = Path(artifact["target"])',
        '        target_dir.mkdir(exist_ok=True, parents=True)\n',
        '        # Expand glob patterns',
        '        # Expand glob patterns\n',
        '        for src_path in glob.glob(src_pattern, recursive=True):\n',
        '            src = Path(src_path)\n',
        '            if not src.exists():\n',
        '                print(f"Warning: Artifact not found: {src}")\n',
        '                continue\n',
        '            target_path = target_dir / src.name\n',
        '            if src.is_file():\n',
        '                shutil.copy2(src, target_path)\n',
        '                print(f"Copied artifact: {src} -> {target_path}")\n',
        '            elif src.is_dir():\n',
        '                shutil.copytree(src, target_path, dirs_exist_ok=True)\n',
        '                print(f"Copied directory: {src} -> {target_path}")\n',
        'def main() -> int:',
        '    try:',
        '        # Create results directory',
        '        results_dir = Path("/results")',
        '        results_dir.mkdir(exist_ok=True, parents=True)\n',
        '        # Set up environment variables',
        '        env = os.environ.copy()',
        '        env.update({',
    ]
    
    # Add environment variables
    env_vars = profile_config.get('environment', {})
    for key, value in env_vars.items():
        lines.append(f'            "{key}": f"{value}",')
    
    lines.extend([
        '        })\n',
        '        # Pre-execute commands',
        '        for cmd_config in [',
    ])
    
    # Add pre-execute commands
    for cmd in profile_config.get('pre_execute', []):
        cmd_str = cmd['command']
        cwd = cmd.get('cwd', '.')
        lines.append(f'            {{"command": {repr(cmd_str)}, "cwd": "{cwd}"}},')
    
    lines.extend([
        '        ]:',
        '            if cmd_config:',
        '                cmd_parts = cmd_config["command"].split()',
        '                cwd = cmd_config.get("cwd", ".")',
        '                print(f"Running pre-execute: {cmd_parts} in {cwd}")',
        '                return_code = run_command(cmd_parts, cwd=cwd, env=env)',
        '                if return_code != 0:',
        '                    print(f"Pre-execute command failed with code {return_code}", file=sys.stderr)',
        '                    return return_code\n',
        '        # Main execution',
        '        exec_config = ' + repr(profile_config.get('execute', {})) + '\n',
        '        if exec_config:',
        '            cmd = exec_config.get("command", "").split()',
        '            if exec_config.get("args"):',
        '                cmd.extend(exec_config["args"])',
        '            cwd = exec_config.get("cwd", ".")',
        '            timeout = exec_config.get("timeout", 300)',
        '            print(f"Running main command: {cmd} in {cwd}")',
        '            return_code = run_command(cmd, cwd=cwd, env=env, timeout=timeout)\n',
        '        # Post-execute commands',
        '        for cmd_config in [',
    ])
    
    # Add post-execute commands
    for cmd in profile_config.get('post_execute', []):
        cmd_str = cmd['command']
        cwd = cmd.get('cwd', '.')
        lines.append(f'            {{"command": {repr(cmd_str)}, "cwd": "{cwd}"}},')
    
    lines.extend([
        '        ]:',
        '            if cmd_config:',
        '                cmd_parts = cmd_config["command"].split()',
        '                cwd = cmd_config.get("cwd", ".")',
        '                print(f"Running post-execute: {cmd_parts} in {cwd}")',
        '                cmd_return_code = run_command(cmd_parts, cwd=cwd, env=env)',
        '                # Only update return code if it was a success (0) or if we haven\'t had an error yet',
        '                if return_code == 0 and cmd_return_code != 0:',
        '                    return_code = cmd_return_code\n',
        '        # Collect artifacts',
        '        artifacts = ' + repr(profile_config.get('artifacts', [])) + '\n',
        '        if artifacts:',
        '            print("Collecting artifacts...")',
        '            try:',
        '                collect_artifacts(artifacts)',
        '            except Exception as e:',
        '                print(f"Error collecting artifacts: {e}", file=sys.stderr)\n',
        '        return return_code',
        '    except Exception as e:',
        '        print(f"Error: {e}", file=sys.stderr)',
        '        return 1\n',
        'if __name__ == "__main__":',
        '    sys.exit(main())',
    ])
    
    return '\n'.join(lines)


def generate_shim(config_path: str = ".gitinsiderc.yaml", output_path: str = "shim.py", profile: str = "default") -> None:
    """Generate a shim script based on the configuration."""
    config = load_config(config_path)
    shim_script = generate_shim_script(config, profile)
    
    with open(output_path, 'w') as f:
        f.write(shim_script)
    
    # Make the script executable
    os.chmod(output_path, 0o755)
    print(f"Generated shim script at {output_path}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate a shim script based on .gitinsiderc.yaml')
    parser.add_argument('--config', default=".gitinsiderc.yaml", help='Path to the configuration file')
    parser.add_argument('--output', default="shim.py", help='Output path for the generated shim script')
    parser.add_argument('--profile', default="default", help='Profile to use from the configuration')
    
    args = parser.parse_args()
    
    try:
        generate_shim(args.config, args.output, args.profile)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
