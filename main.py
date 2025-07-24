import os
import sys
import uvloop
import shutil
import asyncio
import logging
import subprocess
from bot import Bot
from git import Repo
from pyrogram.methods.utilities.idle import idle

from config import Config

plugins_folder = Config.getenv("plugins_folder", "plugins")


async def main():
    app = Bot(
        "data/" + str(Config.getenv("client_name", "itisFarzin")),
        api_id=Config.getenv("api_id"),
        api_hash=Config.getenv("api_hash"),
        bot_token=Config.getenv("bot_token"),
        proxy=Config.url_parser(Config.PROXY, is_a_proxy=True),
        plugins=dict(root=plugins_folder),
    )
    await app.start()
    await idle()
    await app.stop()


def requirements():
    for dirpath, __, filenames in os.walk(plugins_folder, followlinks=True):
        if "requirements.txt" in filenames:
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--upgrade",
                    "--disable-pip-version-check",
                    "-r",
                    os.path.join(dirpath, "requirements.txt"),
                ],
            )


def setup_plugins():
    plugins_repo = Config.getenv(
        "plugins_repo", "https://github.com/6AMStuff/itisFarzinBotPlugins"
    )
    if not plugins_repo:
        logging.warning("Skipping setting up plugins.")
        return

    repo_name = os.path.basename(plugins_repo).replace(".git", "")
    repo_path = os.path.join(plugins_folder, repo_name)
    if os.path.exists(repo_path):
        repo = Repo(repo_path)
        if plugins_repo not in [remote.url for remote in repo.remotes]:
            logging.warning(
                f"{repo_name} doesn't have {plugins_repo}"
                " as one of its remotes."
            )
            logging.info(f"Removing {repo_name}'s folder.")
            shutil.rmtree(repo_path)
            Repo.clone_from(plugins_repo, repo_path)
            logging.info(f"Cloned {repo_name}.")

        repo.remote().fetch()
        repo.git.pull()
        logging.info(f"Updated {repo_name}.")
    else:
        Repo.clone_from(plugins_repo, repo_path)
        logging.info(f"Cloned {repo_name}.")


if __name__ == "__main__":
    setup_plugins()

    if Config.getenv("test_mode") not in {"true", "1"}:
        requirements()

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    asyncio.run(main())
