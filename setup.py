#!/usr/bin/env python3
import os
import shutil
import argparse
import subprocess

parser = argparse.ArgumentParser(
    prog="setup.py", description="Help to set up basics"
)

parser.add_argument(
    "--verbose", action=argparse.BooleanOptionalAction, default=True
)
parser.add_argument("--requirement", type=str, default="requirements.txt")

args = parser.parse_args()


def setup_environment(requirement="requirements.txt", verbose=True):
    pip_command = [
        "pip",
        "install",
        "--disable-pip-version-check",
        "--upgrade",
        "--requirement",
        requirement or "",
    ]

    if os.path.exists("/IS_CONTAINER"):
        if verbose:
            print("Running in a container")
        pip_command += [
            "--no-cache-dir",
            "--break-system-packages",
            "--root-user-action",
            "ignore",
        ]
    else:
        if verbose:
            print("Running in a normal environment")
            print("Setting virtual environment up")
        os.system("python -m venv venv")
        os.system("source venv/bin/activate")

    if verbose:
        print("Installing dependencies")
    else:
        pip_command.append("-q")

    if requirement:
        subprocess.call(pip_command)


if __name__ == "__main__":
    setup_environment(args.requirement, args.verbose)

    if not os.path.isfile("data/.env"):
        shutil.copy("data/.env.example", "data/.env")
        if args.verbose:
            print("Copied .env.example to .env")
