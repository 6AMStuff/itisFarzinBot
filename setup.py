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
parser.add_argument(
    "--optional-requirement", type=str, default="requirements-optional.txt"
)

args = parser.parse_args()


def setup_environment(requirement="requirements.txt", verbose=True):
    if not requirement or not os.path.exists(requirement):
        print(f"WARNING: {requirement} doesn't exist!")
        return

    requirements = []
    optional = "optional" in requirement

    pip_command = [
        "pip",
        "install",
        "--disable-pip-version-check",
        "--upgrade",
    ]

    if os.path.exists("/IS_CONTAINER"):
        if verbose:
            print("Running in a container")
        pip_command += [
            "--no-cache-dir",
            "--break-system-packages",
            "--no-warn-script-location",
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

    with open(requirement, "r") as f:
        requirements = f.readlines()

    if optional:
        for req in requirements:
            subprocess.call(pip_command + [req])
    else:
        subprocess.call(pip_command + requirements)


if __name__ == "__main__":
    setup_environment(args.requirement, args.verbose)
    setup_environment(args.optional_requirement, False)

    if not os.path.isfile("data/.env"):
        shutil.copy("data/.env.example", "data/.env")
        if args.verbose:
            print("Copied .env.example to .env")
