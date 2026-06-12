#!/usr/bin/env python3
"""Bootstrap launcher for lanhu-skill.

Creates a private virtual environment on first use, installs requirements, then
delegates all subcommands to ``lanhu_cli.py``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import venv


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
VENV_DIR = SKILL_DIR / ".venv"
STATE_FILE = VENV_DIR / ".lanhu_skill_state.json"
REQUIREMENTS_FILE = SCRIPT_DIR / "requirements.txt"
CLI_SCRIPT = SCRIPT_DIR / "lanhu_cli.py"
COOKIE_OPTIONAL_COMMANDS = {"classify-url"}
EXTERNAL_MCP_ENV = "LANHU_MCP_COMMAND"


def _venv_python() -> Path:
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def _detect_external_mcp() -> list[str] | None:
    configured = os.environ.get(EXTERNAL_MCP_ENV)
    if configured:
        return [configured]
    resolved = shutil.which("lanhu-mcp")
    if resolved:
        return [resolved]
    return None


def _requirements_hash() -> str:
    return hashlib.sha256(REQUIREMENTS_FILE.read_bytes()).hexdigest()


def _load_state() -> dict:
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _save_state(state: dict) -> None:
    VENV_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def _run(cmd: list[str]) -> None:
    completed = subprocess.run(cmd, check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"Command failed with exit code {completed.returncode}: {' '.join(cmd)}")


def _ensure_venv_exists() -> None:
    if _venv_python().exists():
        return
    builder = venv.EnvBuilder(with_pip=True)
    builder.create(VENV_DIR)


def _needs_install(state: dict) -> bool:
    if not _venv_python().exists():
        return True
    if state.get("requirements_hash") != _requirements_hash():
        return True
    if not state.get("dependencies_installed"):
        return True
    return False


def _install_dependencies(state: dict) -> None:
    python = str(_venv_python())
    _run([python, "-m", "pip", "install", "--upgrade", "pip"])
    _run([python, "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)])
    _run([python, "-m", "playwright", "install", "chromium"])
    state.update(
        {
            "requirements_hash": _requirements_hash(),
            "dependencies_installed": True,
            "playwright_browser": "chromium",
        }
    )
    _save_state(state)


def _delegate(command: list[str]) -> int:
    python = str(_venv_python())
    result = subprocess.run([python, str(CLI_SCRIPT), *command], check=False)
    return result.returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Lanhu skill bootstrap with auto-install support."
    )
    parser.add_argument(
        "--dry-run-install",
        action="store_true",
        help="Only print the auto-install and command delegation plan.",
    )
    parser.add_argument(
        "--skip-install",
        action="store_true",
        help="Do not auto-install dependencies; fail fast if the environment is not ready.",
    )
    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="Subcommand and arguments forwarded to lanhu_cli.py",
    )
    return parser


def _requires_cookie(command: list[str]) -> bool:
    if not command:
        return False
    return command[0] not in COOKIE_OPTIONAL_COMMANDS


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    command = args.command
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        parser.print_help()
        return 0

    state = _load_state()
    payload = {
        "status": "dry_run" if args.dry_run_install else "ready",
        "auto_install": not args.skip_install,
        "venv_dir": str(VENV_DIR),
        "requirements": str(REQUIREMENTS_FILE),
        "command": command,
        "external_mcp_available": bool(_detect_external_mcp()),
    }

    if args.dry_run_install:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    external_command = _detect_external_mcp()
    if external_command:
        print(
            json.dumps(
                {
                    "status": "external_mcp_detected",
                    "message": "Detected external lanhu-mcp. Skip lanhu-skill local bootstrap.",
                    "external_command": external_command,
                    "command": command,
                },
                ensure_ascii=False,
            )
        )
        return 0

    if _requires_cookie(command) and not os.environ.get("LANHU_COOKIE"):
        print(
            json.dumps(
                {
                    "status": "error",
                    "message": "Missing required environment variable: LANHU_COOKIE",
                    "required_env": ["LANHU_COOKIE"],
                    "command": command,
                },
                ensure_ascii=False,
            )
        )
        return 1

    _ensure_venv_exists()
    state = _load_state()
    if _needs_install(state):
        if args.skip_install:
            print(
                json.dumps(
                    {
                        "status": "error",
                        "message": "Lanhu skill dependencies are not installed.",
                        "venv_dir": str(VENV_DIR),
                        "requirements": str(REQUIREMENTS_FILE),
                    },
                    ensure_ascii=False,
                )
            )
            return 1
        _install_dependencies(state)

    return _delegate(command)


if __name__ == "__main__":
    raise SystemExit(main())
