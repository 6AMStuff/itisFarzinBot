#!/usr/bin/env python3
import os
import shutil
import argparse
import subprocess

parser = argparse.ArgumentParser(
    prog="setup.py",
    description="Help to set up basics"
)

parser.add_argument(
    "--verbose",
    action=argparse.BooleanOptionalAction,
    default=True
)
parser.add_argument("--requirement", type=str, default="requirements.txt")

args = parser.parse_args()

pip_command = [
    "pip",
    "install",
    "--disable-pip-version-check",
    "--upgrade",
    "--requirement",
    args.requirement or ""
]

if os.path.exists("/IS_CONTAINER"):
    if args.verbose:
        print("Running in a container")
    pip_command += [
        "--no-cache-dir",
        "--break-system-packages",
        "--root-user-action",
        "ignore"
    ]
else:
    if args.verbose:
        print("Running in a normal environment")
        print("Setting virtual environment up")
    os.system("python -m venv venv")
    os.system("source venv/bin/activate")

if args.verbose:
    print("Installing dependencies")
else:
    pip_command.append("-q")

if args.requirement:
    subprocess.call(pip_command)

if not os.path.isfile("data/.env"):
    shutil.copy("data/.env.example", "data/.env")
    if args.verbose:
        print("Copied .env.example to .env")
