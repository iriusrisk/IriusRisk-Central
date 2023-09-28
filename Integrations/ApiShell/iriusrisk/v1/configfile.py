from enum import Enum
import configparser
import logging
import os
import platform

# Automatically loaded and executed when this module is loaded.
# 
# Provides hierarchical searching and loading of configuration files.
#
# TODO Currently only finds config file in the current working directory. Need
# to add the user data directory and global data directory, in a cross-platform manner.
#
# See https://docs.python.org/3/library/configparser.html

# Mac:
#   - User: $HOME/.iriusrisk/iriusrisk.ini
#   - Global: ??? /usr/Shared/.iriusrisk/iriusrisk.ini
#
# Win:
#   - User: %LocalAppDataFolder%/.iriusrisk/iriusrisk.ini
#   - Global: %AppDataFolder%/.iriusrisk/iriusrisk.ini
# 
# Linux:
#   - User:

_log = logging.getLogger("iriusrisk.v1")

class _Which(Enum):
    HOME = 1
    GLOBAL = 2

def _get_for_darwin(which):
    if which == _Which.GLOBAL:
        return "/Users/Shared"
    elif which == _Which.HOME:
        if "HOME" in os.environ:
            return os.environ["HOME"]
    
    return None

def _get_for_linux(which):
    if which == _Which.GLOBAL:
        return "/etc"
    elif which == _Which.HOME:
        if "HOME" in os.environ:
            return os.environ["HOME"]

        return "~"
    
    return None

def _get_for_windows(which):
    if which == _Which.GLOBAL:
        if "AppDataFolder" in os.environ:
            return os.environ["AppDataFolder"]
    elif which == _Which.HOME:
        if "LocalAppDataFolder" in os.environ:
            return os.environ["LocalAppDataFolder"]
        
        return "~"

    return None

def _get_for_java(which):
    return _default_get(which)

def _default_get(which):
    if which == _Which.HOME:
        return "~"

    return None

paths = {
    'Darwin': _get_for_darwin,
    'Linux': _get_for_linux,
    'Windows': _get_for_windows,
    'Java': _get_for_java
}

def _add(locations, callback, which):
    next = callback(which)
    if next:
        locations.append(f"{next}/.iriusrisk/iriusrisk.ini")

def parse_config():
    sys = platform.system()
    if sys in paths:
        _log.info(f"Getting system information for {sys}")
        _get_var = paths[sys]
    else:
        _log.warning("System not recognized: {sys}")
        _get_var = _default_get

    locations = []
    _add(locations, _get_var, _Which.GLOBAL)    
    _add(locations, _get_var, _Which.HOME)
    locations.append("iriusrisk.ini")

    _log.info(f"Looking for configuration files in {len(locations)}(s)")
    if len(locations) > 0 and _log.isEnabledFor(logging.DEBUG):
        _log.debug("Locations that will be tried (in this order):")
        for location in locations:
            _log.debug(f"  {location}")

    config = configparser.ConfigParser()
    files = config.read(locations)
    _log.info(f"Found a total of {len(files)} configuration file(s)")
    if len(files) == 0:
        return None
    
    if _log.isEnabledFor(logging.DEBUG):
        _log.debug("Configuration files actually found:")
        for file in files:
            _log.debug(f"  {file}")

    return config