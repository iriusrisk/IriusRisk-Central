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
entries useful for making IriusRisk API calls. Most of the command line 
arguments provided can be duplicated in configuration files, thereby allowing
you to providethem in a file once across multiple script calls.

Configuration files are always named "iriusrisk.ini" and are searched for in
the following locations:

  * {working directory}/iriusrisk.ini
  * {user data directory}/.iriusrisk/iriusrisk.ini
  * {global data directory}/.iriusrisk/iriusrisk.ini

There is a precedence for the ini files; the first one overrides, the next, and
so on. Hence, the same keys may appear in multiple ini files, but the one
"nearest" to the script will be used.

Command line arguments take precedence over ini files. The verbosity parameters
(verbose and quiet) are only available on the command line.



"""), epilog=textwrap.dedent(
"""***************************************************
Format and contents of the initialization files

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

A note regarding URLs:
When accessing a HTTP server, Python expects a URL that contains the domain and
port number, but no protocol. For most users, the complexity of this can be
ignored completely. For instance, if you are accessing a IriusRisk instance
provided as SaaS by IriusRisk, you only need to provide the --subdomain of the
instance. For instance, if your IriusRisk instance has a URL as follows:

    https://my-company.iriusrisk.com/

you need only provide the subdomain parameter on the command line or in a config
file:

    --subdomain my-company

If instead, you have a non-IriusRisk domain hosting your instance, you can 
specify this using the domain parameter:

    --domain ir-subdomain.example.com

Finally, the url parameter can be used for URLs that don't follow this simple
pattern. Note that when using the url parameter, you may not include a
protocol (e.g., https), but you must supply the port number. For instance:

    --url subdomain.example.com:443/iriusrisk

The port parameter can be used when leveraging the domain parameter. It defaults
to 443. Only one of the parameters subdomain, domain and url are recognized.
"""
))
    parser.add_argument("-k", "--key", help="API Token to use when accessing the API")
    parser.add_argument("-s", "--subdomain", help="Subdomain of a SaaS instance. Will be prepended to .iriusrisk.com")
    parser.add_argument("-d", "--domain", help="The entire domain of the target system, without protocol or path.")
    parser.add_argument("-p", "--port", help="Defaults to 443.")
    parser.add_argument("-u", "--url", help="Enter the entire base URL for the target system. Cannot have protocol, but must have port.")
    parser.add_argument("-v", "--verbose", help="Output extended log information", action='store_true')
    parser.add_argument("-q", "--quiet", help="Only output log messages indicating errors", action='store_true')
    parser.add_argument("--dryrun", help="Do everything but actual HTTP calls", action='store_true')
    return parser