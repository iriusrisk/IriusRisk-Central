import argparse
import textwrap

# Automatically loaded and executed when this module is loaded.
# 
# Parses the command line. Arguments can be added by adding another parser#add_argument() call.
#
# See https://docs.python.org/3/library/argparse.html

def get_parser():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, 
                                     description=textwrap.dedent(
"""IriusRisk Script Shell

This is a program shell to aid calling IriusRisk APIs. Use this shell to 
create more complex scripts that create, call and process API calls.

Using this shell program provides default command-line and configuration-file
entries useful for making IriusRisk API calls. Some of the command line 
arguments can appear in configuration files, thereby allowing them to be
specified across multiple script calls.

Configuration files are always named "iriusrisk.ini" and are searched for in
the following locations:

  * {working directory}/iriusrisk.ini
  * {user data directory}/.iriusrisk/iriusrisk.ini
  * {global data directory}/.iriusrisk/iriusrisk.ini

The same keys may appear in multiple ini files, but the one "nearest" to the
script will be used. For instance, if the same key appears in the ini file
in the working directory and the in the user data directory, the one in the 
working directory takes precedence.

Command line arguments take precedence over ini files. 

"""), epilog=textwrap.dedent(
"""***************************************************
Each ini file contains a default namespace that must be explicitly declared.
Within this namespace are zero or more key/value pairs, corresponding to the
command line arguments. Format is as follows:

    [DEFAULT]
    key1 = value1
    key2 = value2

The key names correspond to the command line parameters, without any hyphens.
So specifying the API key in a config file would look something like this:

    [DEFAULT]
    key = a123b456-78c9-01d2-e345-f6789ab012c3
"""
))
    parser.add_argument("-s", "--subdomain", help="Subdomain of a SaaS instance. Will be prepended to .iriusrisk.com")
    parser.add_argument("-d", "--domain", help="The entire domain of the target system, without protocol or path.")
    parser.add_argument("-f", "--full-url", help="The target system's complete URL, port number included, but no protocol.")
    parser.add_argument("-v", "--verbose", help="Output extended log information", action='store_true')
    parser.add_argument("-q", "--quiet", help="Only output log messages indicating errors", action='store_true')
    parser.add_argument("--dryrun", help="Do everything but actual HTTP calls", action='store_true')
    return parser