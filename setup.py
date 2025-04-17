#!/usr/bin/env python3
import os
import shutil

if not os.path.isfile("data/.env"):
    shutil.copy("data/.env.example", "data/.env")
