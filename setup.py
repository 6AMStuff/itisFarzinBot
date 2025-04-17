#!/usr/bin/env python3
import os
import shutil
import subprocess

pip_command = [
    "pip",
    "install",
    "--upgrade",
    "--requirement",
    "requirements.txt"
]

if os.path.exists("/IS_CONTAINER"):
    pip_command += ["--no-cache-dir", "--break-system-packages"]
else:
    os.system("python -m venv venv")
    os.system("source venv/bin/activate")

subprocess.call(pip_command)

if not os.path.isfile("data/.env"):
    shutil.copy("data/.env.example", "data/.env")
