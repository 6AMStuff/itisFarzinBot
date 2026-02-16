# itisFarzinBot

A lightweight, modular Telegram bot framework built on [Kurigram](https://docs.kurigram.live/).

## Features

- **Modularity**: Features are each as an isolated plugins.
- **Docker**: Can be run as a Docker container.

## Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager
- [Telegram API credentials](https://my.telegram.org/apps)

## Installation

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/6AMStuff/itisFarzinBot.git
cd itisFarzinBot
```

2. Install dependencies:
```bash
uv sync
```

3. Configure your bot by creating a `config/` directory with the necessary configuration files. See the example configuration files for reference.

### Docker

Pull the latest image from GitHub Container Registry:
```bash
docker pull ghcr.io/6amstuff/itisfarzinbot:latest
```

## Running

### Local Development

Run the bot using uv:
```bash
uv run python main.py
```

### Docker

Run the bot using Docker:
```bash
docker run -d \
  --name itisfarzinbot \
  -v ./config:/app/config \
  -v ./plugins:/app/plugins \
  ghcr.io/6amstuff/itisfarzinbot:latest
```

## Plugins

Users can expand their bot's functionality by obtaining plugins from the official repository: [itisFarzinBotPlugins](https://github.com/6AMStuff/itisFarzinBotPlugins).

## Contributing

Contributions to the main bot framework are welcome! Please open issues or submit pull requests for enhancements or bug fixes. For plugin development, please refer to the plugins repository.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
