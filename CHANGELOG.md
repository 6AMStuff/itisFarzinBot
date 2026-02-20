## v0.17.1 (2026-02-20)

### Features

- **types**: add custom message type stub
- **core**: import dispatcher

### Bug Fixes

- **dispatcher**: correct update process

### Code Refactoring

- **core**: remove commented-out code
- **core**: move notify_module to plugin manager
- **bot**: prepare for mypy strict
- **core**: prepare for mypy strict
- **types**: prepare for mypy strict
- **plugins**: prepare for mypy strict
- **settings**: prepare for mypy strict

### Maintenance

- **commitizen**: update configurations
- **mypy**: enable strict mode
- **pyproject**: add mypy
- **pyproject**: add ruff

### Styling

- **itisfarzinbot**: reformat to satisfy ruff

## v0.17.0 (2026-02-16)

### Features

- **itisfarzinbot**: switch to uv

### Maintenance

- **docker**: bind pip to uv pip
- **pyproject**: define project
- **commitizen**: remove the old config
- **pyproject**: set up commitizen

### Documentation

- **readme**: update prerequisites, add installation and running sections

### Build System

- **docker**: move uv pip wrapper into images

## v0.16.2 (2026-02-04)

### BREAKING CHANGE

- Every instance of settings should be changed to bot.settings

### Bug Fixes

- **plugin-manager**: skip dot-prefixed directories in plugins

### Code Refactoring

- **settings**: correct an invalid return value
- **bot**: make pyright happy
- **settings**: move it under project
- **plugins/data**: make pyright happy
- **plugins/manager**: make pyright happy
- **plugin-manager**: make pyright happy
- **settings**: make pyright happy

## v0.16.1 (2026-01-27)

### Code Refactoring

- **main**: drop default values when calling getenv
- **settings**: drop default values when calling getenv

### Build System

- **deps**: update kurigram to 2.2.17
- **docker**: chown to 1000:1000 in copies

## v0.16.0 (2025-12-28)

### BREAKING CHANGE

- Removed directories /config and /plugins; use /app/config and /app/plugins instead.

### Build System

- **docker**: correct mkdir command
- **docker**: update python environments
- **docker**: update labels
- **docker**: update volumes
- **docker**: include the config.sample.yaml file

### Continuous Integration

- **docker**: parallelize docker builds

## v0.15.3 (2025-12-27)

### Bug Fixes

- **main**: correct the requirements setup logic

## v0.15.2 (2025-12-07)

### Continuous Integration

- **github**: change the minimal tag to {branch}-minimal
- **github**: add workflow support for the minimal variant
- **docker**: add minimal variant

## v0.15.1 (2025-12-06)

### Build System

- **docker**: use python:3.13-alpine3.21 as the base image

## v0.15.0 (2025-12-06)

### Code Refactoring

- **plugin-manager**: rename set_plugin_status to set_plugins_status
- **plugin-manager**: minor code cleanups and improvements
- **plugin-manager**: enhance handling of empty plugins variables
- **plugin-manager**: remove the unreachable code from unload_plugins
- **settings**: use any for unspecified variable types
- **settings**: remove the unnecessary .to_str
- **settings**: replace optionals with nones
- **plugin-manager**: replace optionals with nones
- **plugin-manager**: drop the useless code in unload_plugins
- **plugin-manager**: remove the unreachable code from load_plugins
- **plugin-manager**: improve get_plugins
- **plugin-manager**: improve get_handlers
- **plugin-manager**: improve unload_plugins
- **plugin-manager**: improve load_plugins
- **plugin-manager**: improve modules_list
- **plugins/data**: little improvements for notify_module

### Build System

- **deps**: update `kurigram` to 2.2.15

## v0.14.4 (2025-11-10)

### Bug Fixes

- **settings**: update the default configurations

### Code Refactoring

- **settings**: improve the value class

### Styling

- **settings**: reformat code with black

## v0.14.3 (2025-11-03)

### Code Refactoring

- **deps**: add the default configurations

### Build System

- **docker**: cleaner user and ownership setup

## v0.14.2 (2025-10-26)

### Features

- **main**: add disable requirements setup config

## v0.14.1 (2025-10-09)

### Bug Fixes

- **settings**: use the environment's value in getdata
- **settings**: treat nones as empty strings

### Build System

- **deps**: update `GitPython` to 3.1.45
- **deps**: update `SQLAlchemy` to 2.0.43
- **deps**: update `kurigram` to 2.2.12

## v0.14.0 (2025-09-18)

### BREAKING CHANGE

- duh
- Rename the folder
- Migrate to yaml from .env

### Features

- **main**: clone the plugins repository based on the current branch
- **settings**: add value class
- **settings**: switch to yaml for the config file
- **main**: add in_memory support

### Code Refactoring

- **config**: drop it
- **core**: switch to settings from config
- **main**: adapt to the new getenv
- rename data folder to config
- **settings**: change admins delimiter to a space

### Styling

- **manager**: reformat code with black

### Build System

- **docker**: add version environment
- **deps**: update `kurigram` to 2.2.10
- **docker**: set in_memory to true
- **docker**: update labels

### Continuous Integration

- **github**: update docker tags
- **github**: add caching to docker workflow
- **github**: overhaul the docker workflow

## v0.13.3 (2025-07-28)

### BREAKING CHANGE

- TZ got replaced with tz in the config file

### Features

- **settings**: check for https proxy in proxy variable
- **settings**: add test mode variable
- **main**: auto set up plugins

### Bug Fixes

- **settings**: use os instead of settings for `_tz`'s getenv

### Code Refactoring

- **plugin-manager**: `config` to `settings`
- **settings**: deduplicate logging text and date format
- **settings**: use lowercase tz variable value for timezone
- **main**: `config` to `settings`
- **settings**: timezone clean up
- **main**: log requirements installations to log file

### Styling

- **settings**: manual and black reformat

### Continuous Integration

- **github**: fetch all commits
- **github**: update docker tag naming convention

## v0.13.2 (2025-07-23)

### Features

- **manager**: support cli

### Bug Fixes

- **plugin-manager**: handle non-pyrogram handlers

### Code Refactoring

- **drop-example-plugins**: the built-in plugins are good examples by themselves
- change `__all__` from list to tuple
- **.env.example**: update example values and improve clarity
- **settings**: use any and optional types
- **data**: mark as not bot only

### Styling

- **main**: reformat with black
- **pre-commit**: exclude .venv from linting

### Documentation

- **readme**: completely overhaul the content

### Build System

- **deps**: update `python-dotenv` to 1.1.1
- **deps**: update `sqlalchemy` to 2.0.41
- **deps**: update `kurigram` to 2.2.7
- **docker**: add the source label
- **docker**: add labels
- **docker**: exclude data and plugin directories
- **docker**: chown `/opt/venv` to user and group `abc`

### Continuous Integration

- **github**: add 6-letter commit SHA to dev branch builds
- **github**: set `BUILD_DATE` in build system
- **github**: improve repository name handling
- **github**: add docker build and push

## v0.13.1 (2025-07-08)

### Features

- **main**: add requirements installer

### Code Refactoring

- improve docker structure and remove setup.py

## v0.13.0 (2025-06-27)

### Bug Fixes

- **setup**: don't report environments on optional requirements

### Code Refactoring

- **core**: move plugin related methods to its own class

### Build System

- **docker**: add git package

## v0.12.3 (2025-06-17)

### Features

- **bot**: add `is_bot` and `__bot_only__` for plugins

### Bug Fixes

- **setup**: disable verbose for optional requirements

### Code Refactoring

- **main**: improve uvloop and initialization setup

### Build System

- **deps**: update `kurigram` to 2.2.6

## v0.12.2 (2025-06-14)

### Build System

- **docker**: install gcc and required dependencies
- **docker**: switch back to alpine
- **setup**: add support for optional packages

## v0.12.1 (2025-06-12)

### Features

- **bot**: use uvloop instead of built-in asyncio
- **bot**: add uptime variable

### Build System

- **deps**: update `kurigram` to 2.2.5

## v0.12.0 (2025-06-08)

### Features

- **deps**: [TMP] update `kurigram` to `4db3f39`

### Build System

- **docker**: switch to python 3.13-slim
- **deps**: update `kurigram` to 2.2.4

## v0.11.10 (2025-05-28)

### Features

- **settings**: add support for timezones

## v0.11.9 (2025-05-25)

### Features

- **settings**: improve logging

### Bug Fixes

- **settings**: correct proxy variable type for None

### Code Refactoring

- **settings**: config.py -> settings.py

### Build System

- **deps**: add socksio package

## v0.11.8 (2025-05-21)

### Features

- **bot**: Clamp plugin handler groups at 0
- **settings**: enable pool_pre_ping

### Build System

- **deps**: add PyMySQL package

## v0.11.7 (2025-05-17)

### Bug Fixes

- **manager**: add admin filter to plugins callback

## v0.11.6 (2025-05-16)

### Bug Fixes

- **settings**: correct a nested double quotes
- **manager**: support - (dash) in plugins callback regex

### Build System

- **docker**: rewrite the build system

## v0.11.5 (2025-05-15)

### Build System

- **docker**: improved structure

## v0.11.4 (2025-05-15)

### Bug Fixes

- **manager**: handle when there is no plugin in `plugins` command

### Code Refactoring

- **settings**: Allow passing plugin name to data methods

## v0.11.3 (2025-05-15)

### Build System

- **dependencies**: update `kurigram` to 2.2.3

## v0.11.2 (2025-05-15)

### Bug Fixes

- **config**: exclude venv folder from flake8 in pre commit

## v0.11.1 (2025-05-15)

### Features

- **config**: add pyproject.toml support for flake8

### Styling

- reformat code with black

## v0.11.0 (2025-05-15)

### Features

- **config**: configure pre commit
- **config**: configure black and flake8

### Styling

- **commitizen**: update changelog on bump
- **commitizen**: set up Commitizen

## v0.10.2 (2025-05-15)

### Code Refactoring

- **manager**: replace plugin's name '-' and '_' with spaces when displaying

## v0.10.1 (2025-05-15)

### Bug Fixes

- **plugins**: create databse tables before loading plugins
- **manager**: force plugin loading in plugins command

## v0.10.0 (2025-05-15)

### Features

- create SQL tables after loading plugins
- add test mode

### Bug Fixes

- **manager**: improve plugins command UI

### Code Refactoring

- **manager**: merge `load` and `unload` commands into a single function

## v0.9.1 (2025-05-15)

### Features

- ignore the data's content folder except for `.env.example`

## v0.9.0 (2025-05-15)

### Features

- **plugins**: implement `on_data_change` hook
- create database for missing plugin data
- move log file to data folder
- install dependencies of plugins
- **setup.py**: support for custom requirements file path
- **setup.py**: do not check for a new version of pip
- **setup.py**: Add verbose

### Code Refactoring

- **plugins**: update `notify_module_data_change` to use `modules_list`
- **plugins**: decompose `plugin_list` into focused functions
- **setup.py**: move environment setup to a function and update entry point
- rename `plugin_folder` to `plugins_folder`

## v0.8.0 (2025-05-15)

### Features

- **Docker**: include `data` folder and `requirements.txt` file in image
- **Docker**: include `data/.env.example` in image
- **Docker**: run `setup.py` to set up things
- **setup.py**: Suppress pip warnings
- **setup.py**: install requirements packages
- **Docker**: touch `/IS_CONTAINER` file
- add `setup.py`
- **Docker**: ignore `data` folder
- **Docker**: add .dockerignore
- **treewide**: update dependencies
- **Docker**: switch to python's container as the base

### Maintenance

- Flake8

## v0.7.0 (2025-05-15)

### Features

- only list plugins in plugins command
- only built-in plugins can have lower groups
- add `__all__` to all of plugins

### Maintenance

- change copyright owner's name to my real name

## v0.6.0 (2025-05-15)

### Features

- monospace the value of data
- update dependencies
- rename to `itisFarzinBot`
- ability to search inside of multiple folders for plugins

## v0.5.1 (2025-05-15)

### Features

- ignore `downloads` folder

## v0.5.0 (2025-05-15)

### Features

- add support for using symlink folders for plugins
- add regex version of cmd prefixes

## v0.4.2 (2025-05-15)

### Features

- add data plugin as a builtin plugin

### Bug Fixes

- wrong return type for getdata and deldata

## v0.4.1 (2025-05-15)

### Features

- add ability to get value from env on `getdata`
- use a metaclass for our client class

## v0.4.0 (2025-05-15)

### Features

- add an example plugin for new custom data feature
- add method to remove plugin's custom data
- add custom data row for plugins

### Maintenance

- `only_name` to `path_only` in `plugin_list` function

## v0.3.1 (2025-05-15)

### Features

- add support for disabling load of plugins

## v0.3.0 (2025-05-15)

### Features

- initial of database

## v0.2.0 (2025-05-15)

### Features

- rewrite plugin loader
- rewrite the config file

## v0.1.0 (2025-05-15)

### Features

- My own implementation of plugin loader
- add a wrapper for Client
- add Docker support
- make the log level configurable
- add the plugins folder to gitignore
- make the plugins folder configurable
- initialize BaseBot

### Bug Fixes

- symlink volumes correctly
