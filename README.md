# itisFarzinBot

<p align="center">
  <strong>A lightweight, modular, strictly-typed asynchronous Telegram bot framework built for the modern Python ecosystem.</strong>
</p>

<p align="center">
  <a href="https://app.codacy.com/gh/6AMStuff/itisFarzinBot?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=6AMStuff/itisFarzinBot&amp;utm_campaign=Badge_Grade"><img src="https://api.codacy.com/project/badge/Grade/9d8fde863b17449caeea8b4cc39d6004" alt="Codacy Badge" /></a>
  <a href="https://www.python.org"><img src="https://img.shields.io/badge/python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://github.com/astral-sh/uv"><img src="https://img.shields.io/badge/managed%20by-uv-F43F5E?style=flat-square" alt="uv"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/badge/lint-ruff-000000?style=flat-square" alt="Ruff"></a>
  <a href="https://github.com/facebook/pyrefly"><img src="https://img.shields.io/badge/types-pyrefly-blue?style=flat-square" alt="Type Checked"></a>
  <a href="https://github.com/6AMStuff/itisFarzinBot/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License"></a>
</p>

## Core Architecture

* **Async-First:** Built from the ground up leveraging concurrent, non-blocking I/O operations.
* **Plug & Play Extensibility:** Decoupled core logic supporting dynamic module loading. Seamlessly integrates with the official [itisFarzinBotPlugins](https://github.com/6AMStuff/itisFarzinBotPlugins) ecosystem.
* **Strictly Typed:** Type-hinted codebase passing strict `pyrefly` checks and `ruff` linting.

## Getting Started

### Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager
- Telegram [API credentials](https://my.telegram.org/apps) (`api_id` and `api_hash`)
- A bot token from [@BotFather](https://t.me/BotFather)

### Manual Installation

1. Clone the repository:

```bash
git clone https://github.com/6AMStuff/itisFarzinBot.git
cd itisFarzinBot
```

2. Install dependencies:

```bash
uv sync --locked
```

> For faster MTProto encryption, include the `full` extra: `uv sync --locked --extra full`

3. Configure the bot (see [Configuration](#configuration)).
4. Run the bot:

```bash
uv run -m bot
```

### Docker Setup

Run the bot container:

```bash
docker run -d \
  --name itisfarzinbot \
  -v ./config:/app/config \
  -v ./plugins:/app/plugins \
  ghcr.io/6amstuff/itisfarzinbot:latest
```

## Configuration

The bot reads its settings from `config/config.yaml`. Start from the bundled sample:

```bash
cp config/config.sample.yaml config/config.yaml
```

Then edit `config/config.yaml`. At minimum, set `api_id`, `api_hash`, and `bot_token`.

| Option | Description |
| --- | --- |
| `client_name` | Session name for the Telegram client. |
| `api_id` / `api_hash` | Telegram API credentials from [my.telegram.org](https://my.telegram.org/apps). |
| `bot_token` | Bot token from [@BotFather](https://t.me/BotFather). |
| `in_memory` | Keep the session in memory instead of writing it to disk. |
| `plugins_folder` | Directory plugins are loaded from. |
| `log_level` | Logging level as a Python numeric level (e.g. `20` = `INFO`). |
| `log_max_size_mb` | Maximum size of a log file before it rotates. |
| `log_backup_count` | Number of rotated log files to keep. |
| `admins` | Space-separated list of admin usernames. |
| `tz` | Timezone as an IANA name (e.g. `Europe/London`). |
| `proxy` | Proxy URL for the client (e.g. `socks5://127.0.0.1:8080`). |
| `use_system_proxy` | Fall back to the system proxy when `proxy` is unset. |
| `cmd_prefixes` | Space-separated command prefixes (e.g. `. /`). |
| `db_uri` | SQLAlchemy database URI. |
| `plugins_repo` | Git repository used to fetch plugins. |

## Plugins

Users can expand their bot's functionality by obtaining plugins from the official repository: [itisFarzinBotPlugins](https://github.com/6AMStuff/itisFarzinBotPlugins).

## Development

Install the development dependencies and run the same checks as CI:

```bash
uv sync --locked --extra dev
uv run ruff check        # lint
uv run pyrefly check     # type check
```

Enable the git hooks once to run `ruff`, `pyrefly`, and commit-message checks automatically:

```bash
uv run pre-commit install
```

Commits follow the [Conventional Commits](https://www.conventionalcommits.org) style, enforced on commit by [commitizen](https://commitizen-tools.github.io/commitizen/).

## Contributing

Contributions to the main bot framework are welcome! Please open issues or submit pull requests for enhancements or bug fixes. For plugin development, please refer to the plugins repository.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
