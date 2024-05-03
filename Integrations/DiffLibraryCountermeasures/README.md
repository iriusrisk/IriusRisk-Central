## DiffLibraries program

This looks for differences between two versions of the same library, generally
in two different IriusRisk tenants. By default it looks for differences in all
the libraries, though individual libraries can also be selected.

Output is a CSV file (tab delimited) limited to information about the countermeasures,
specifically the differences between the "left" and "right" versions of the libraries. 
The following columsn our output:

* Library : The reference ID of the library
* Risk Pattern : The risk pattern in which the countermeasure is contained
* Countermeasure : The reference ID of the countermeasure
* State : The relative state of the left and right countermeasures; one of
    * NEW (in the right library but not the left)
    * REMOVED (in the left library but not the right)
    * CHANGED (differences between the two libraries)
    * IDENTICAL (left and right versions are the same) 
* Name : Human-readable name of the countermeasure
* Description : The description
* References : Any registered references
* Test Steps : All the test steps for the countermeasure
* The values associated with UDTs (if present)

### Usage

usage: main.py [-h] --l_key KEY --l_domain DOMAIN [--l_port NUM] --r_key KEY
               --r_domain DOMAIN [--r_port NUM] [-l REF] [-i] [-d] [-q]
               [-o DEST] [--proxy_port NUM] [--proxy_url URL]

Compare libraries of two IriusRisk instances, the 'left' and the 'right' instance. The
domain of the two instances is the fully-qualified domain and subdomain (if present) for 
instances to be searched, without protocol or port. So if the URL of the instance being
logged into is https://iriusrisk.example.com/ui#!login, the domain would be:

    iriusrisk.example.com

and nothing else. Details about a particular library can be parsed by passing in its 
reference. If no reference is specified, then an overview of libraries comparing their 
revision numbers will be output.

options:
  -h, --help            show this help message and exit
  --l_key KEY           The API key for the 'left' instance being queried
  --l_domain DOMAIN     The domain for the 'left' instance being queried
  --l_port NUM          The port number for the 'left' instance; default: 443
  --r_key KEY           The API key for the 'right' instance being queried
  --r_domain DOMAIN     The domain for the 'right' instance being queried
  --r_port NUM          The port number for the 'right' instance; default: 443
  -l REF, --library REF
                        The reference of the library to examine
  -i, --ignore_identical
                        Do not output contents of unchanged libraries
  -d, --debug           Print extended information to stdout/stderr
  -q, --quiet           Only print error messages to stdout
  -o DEST, --output DEST
                        Output results to the indicated file; default:
                        'results.csv'
  --proxy_port NUM      The proxy server port; required if --proxy_url
                        specified
  --proxy_url URL       The proxy server URL, if present

OUTPUT:
Output can be directed to stdout by passing the arguments '-o - -q'. The minus-sign 
passed to the -o parameter indicates output to stdout, while -q ensures that no 
spurious data is output via logs.

The data is output in CSV (tab delimited) format. The columns output are:

    Library         : The library's reference number
    Risk Pattern    : The risk pattern's reference number
    Countermeasure  : The countermeasure's reference number
    State           : How the countermeasure changed (NEW, REMOVED, CHANGED, IDENTICAL)
    Name            : The name of the countermeasure
    Description     : The countermeasure's description
    References      : URLs to any references included on the countermeasure, if any
    Test Steps      : Steps to test whether the countermeasure has mitigated the threat

Note that no data besides the identification is included for REMOVED countermeasures. In
other words, if a countermeasure no longer exists in the right instance, only the references
for the library, risk pattern and countermeasure are included.
