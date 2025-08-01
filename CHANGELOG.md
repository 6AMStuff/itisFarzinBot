## v0.13.3 (2025-07-28)

### BREAKING CHANGE

- TZ got replaced with tz in the config file

### Feat

- **settings**: check for https proxy in proxy variable
- **settings**: add test mode variable
- **main**: auto set up plugins

### Fix

- **settings**: use os instead of settings for `_tz`'s getenv

### Refactor

- **plugin-manager**: `config` to `settings`
- **settings**: deduplicate logging text and date format
- **settings**: use lowercase tz variable value for timezone
- **main**: `config` to `settings`
- **settings**: timezone clean up
- **main**: log requirements installations to log file

## v0.13.2 (2025-07-23)

### Feat

- **manager**: support cli

### Fix

- **plugin-manager**: handle non-pyrogram handlers

### Refactor

- **drop-example-plugins**: the built-in plugins are good examples by themselves
- change `__all__` from list to tuple
- **.env.example**: update example values and improve clarity
- **settings**: use any and optional types
- **data**: mark as not bot only

## v0.13.1 (2025-07-08)

### Feat

- **main**: add requirements installer

### Refactor

- improve docker structure and remove setup.py

## v0.13.0 (2025-06-27)

### Fix

- **setup**: don't report environments on optional requirements

### Refactor

- **core**: move plugin related methods to its own class

## v0.12.3 (2025-06-17)

### Feat

- **bot**: add `is_bot` and `__bot_only__` for plugins

### Fix

- **setup**: disable verbose for optional requirements

### Refactor

- **main**: improve uvloop and initialization setup

## v0.12.2 (2025-06-14)

## v0.12.1 (2025-06-12)

### Feat

- **bot**: use uvloop instead of built-in asyncio
- **bot**: add uptime variable

## v0.12.0 (2025-06-08)

### Feat

- **deps**: [TMP] update `kurigram` to `4db3f39`

## v0.11.10 (2025-05-28)

### Feat

- **settings**: add support for timezones

## v0.11.9 (2025-05-25)

### Feat

- **settings**: improve logging

### Fix

- **settings**: correct proxy variable type for None

### Refactor

- **settings**: config.py -> settings.py

## v0.11.8 (2025-05-21)

### Feat

- **bot**: Clamp plugin handler groups at 0
- **settings**: enable pool_pre_ping

## v0.11.7 (2025-05-17)

### Fix

- **manager**: add admin filter to plugins callback

## v0.11.6 (2025-05-16)

### Fix

- **settings**: correct a nested double quotes
- **manager**: support - (dash) in plugins callback regex

## v0.11.5 (2025-05-15)

## v0.11.4 (2025-05-15)

### Fix

- **manager**: handle when there is no plugin in `plugins` command

### Refactor

- **settings**: Allow passing plugin name to data methods

## v0.11.3 (2025-05-15)

## v0.11.2 (2025-05-15)

### Fix

- **config**: exclude venv folder from flake8 in pre commit

## v0.11.1 (2025-05-15)

### Feat

- **config**: add pyproject.toml support for flake8

## v0.11.0 (2025-05-15)

### Feat

- **config**: configure pre commit
- **config**: configure black and flake8

## v0.10.2 (2025-05-15)

### Refactor

- **manager**: replace plugin's name '-' and '_' with spaces when displaying

## v0.10.1 (2025-05-15)

### Fix

- **plugins**: create databse tables before loading plugins
- **manager**: force plugin loading in plugins command

## v0.10.0 (2025-05-15)

### Feat

- create SQL tables after loading plugins
- add test mode

### Fix

- **manager**: improve plugins command UI

### Refactor

- **manager**: merge `load` and `unload` commands into a single function

## v0.9.1 (2025-05-15)

### Feat

- ignore the data's content folder except for `.env.example`

## v0.9.0 (2025-05-15)

### Feat

- **plugins**: implement `on_data_change` hook
- create database for missing plugin data
- move log file to data folder
- install dependencies of plugins
- **setup.py**: support for custom requirements file path
- **setup.py**: do not check for a new version of pip
- **setup.py**: Add verbose

### Refactor

- **plugins**: update `notify_module_data_change` to use `modules_list`
- **plugins**: decompose `plugin_list` into focused functions
- **setup.py**: move environment setup to a function and update entry point
- rename `plugin_folder` to `plugins_folder`

## v0.8.0 (2025-05-15)

### Feat

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

## v0.7.0 (2025-05-15)

### Feat

- only list plugins in plugins command
- only built-in plugins can have lower groups
- add `__all__` to all of plugins

## v0.6.0 (2025-05-15)

### Feat

- monospace the value of data
- update dependencies
- rename to `itisFarzinBot`
- ability to search inside of multiple folders for plugins

## v0.5.1 (2025-05-15)

### Feat

- ignore `downloads` folder

## v0.5.0 (2025-05-15)

### Feat

- add support for using symlink folders for plugins
- add regex version of cmd prefixes

## v0.4.2 (2025-05-15)

### Feat

- add data plugin as a builtin plugin

### Fix

- wrong return type for getdata and deldata

## v0.4.1 (2025-05-15)

### Feat

- add ability to get value from env on `getdata`
- use a metaclass for our client class

## v0.4.0 (2025-05-15)

### Feat

- add an example plugin for new custom data feature
- add method to remove plugin's custom data
- add custom data row for plugins

## v0.3.1 (2025-05-15)

### Feat

- add support for disabling load of plugins

## v0.3.0 (2025-05-15)

### Feat

- initial of database

## v0.2.0 (2025-05-15)

### Feat

- rewrite plugin loader
- rewrite the config file

## v0.1.0 (2025-05-15)

### Feat

- My own implementation of plugin loader
- add a wrapper for Client
- add Docker support
- make the log level configurable
- add the plugins folder to gitignore
- make the plugins folder configurable
- initialize BaseBot

### Fix

- symlink volumes correctly
