from .is_public_use import IsPublicUse
from .plugin_manager import PluginManager


class Core(PluginManager, IsPublicUse):
    pass


__all__ = ["Core"]
