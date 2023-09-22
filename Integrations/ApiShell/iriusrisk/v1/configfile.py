import configparser

# Automatically loaded and executed when this module is loaded.
# 
# Provides hierarchical searching and loading of configuration files.
#
# TODO Currently only finds config file in the current working directory. Need
# to add the user data directory and global data directory, in a cross-platform manner.
#
# See https://docs.python.org/3/library/configparser.html

def parse_config():
    config = configparser.ConfigParser()
    files = config.read("iriusrisk.ini")
    if len(files) == 0:
        return None

    return config