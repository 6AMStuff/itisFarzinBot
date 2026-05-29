import logging
import os
import shlex
import shutil
import subprocess
from pathlib import Path

import uvloop
from git import Repo
from pyrogram.methods.utilities.idle import idle

from bot import Bot
from bot.settings import Settings

plugins_folder = Settings.getenv("plugins_folder")


async def main() -> None:
    app = Bot(
        "config/" + Settings.getenv("client_name"),
        api_id=Settings.getenv("api_id"),
        api_hash=Settings.getenv("api_hash"),
        bot_token=Settings.getenv("bot_token"),
        in_memory=Settings.getenv("in_memory").is_enabled,
        proxy=Settings.url_parser(Settings.PROXY, is_a_proxy=True),
        plugins=dict(root=plugins_folder),
    )
    await app.start()
    await idle()  # type: ignore[no-untyped-call]
    await app.stop()


def install_requirements(plugins_folder: str) -> None:
    plugins_path = Path(plugins_folder)

    dependency_files: list[Path] = []
    patterns = [
        "requirements.txt", "*/requirements.txt",
        "pyproject.toml", "*/pyproject.toml"
    ]
    for pattern in patterns:
        dependency_files.extend(plugins_path.glob(pattern))

    for dependency_file in dependency_files:
        logging.info(
            f"Installing dependencies for {dependency_file.parent.name}."
        )
        try:
            subprocess.run(  # noqa: S603
                shlex.split(f"uv pip install -r {dependency_file}"),
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            logging.error(
                "Failed to install dependencies for"
                + f" {dependency_file.parent.name}: {e.stderr.strip()}"
            )


def setup_plugins() -> None:
    plugins_repo = Settings.getenv("plugins_repo")
    if not plugins_repo:
        logging.warning("Skipping setting up plugins.")
        return

    repo_name = plugins_repo.rstrip("/").split("/")[-1]
    repo_name = repo_name.removesuffix(".git")

    repo_path = Path(plugins_folder) / repo_name

    try:
        _repo = Repo(".")
        branch = "dev" if _repo.active_branch.name == "dev" else "main"
    except Exception:
        branch = "dev" if os.getenv("VERSION") == "dev" else "main"

    if repo_path.exists():
        repo = Repo(repo_path)
        if plugins_repo not in [remote.url for remote in repo.remotes]:
            logging.warning(
                f"{repo_name} doesn't have {plugins_repo}"
                " as one of its remotes."
            )
            logging.info(f"Removing {repo_name}'s folder.")
            shutil.rmtree(repo_path)
            Repo.clone_from(plugins_repo, repo_path, branch=branch)
            logging.info(f"Cloned {repo_name}.")

        repo.remote().fetch()
        repo.git.pull()
        logging.info(f"Updated {repo_name}.")
    else:
        Repo.clone_from(plugins_repo, repo_path, branch=branch)
        logging.info(f"Cloned {repo_name}.")


if __name__ == "__main__":
    setup_plugins()

    if (
        not Settings.TEST_MODE
        and not Settings.getenv("disable_requirements").is_enabled
    ):
        install_requirements(plugins_folder)

    uvloop.run(main())
