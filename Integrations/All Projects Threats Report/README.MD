# Purpose 

The purpose of this script is to pull a set of threats, their respective countermeasures and several additional values and output them to a json output file. 

# Requirements

1. Config file with the following values defined in the same directory: 

```python
  api_key = '{your_api_key}'
  sub_domain = '{your_full_domain_minus_the_api_endpoint_data}' # for example https://demo.iriusrisk.com
```

2. Install the required packages

```python
    pip install requests
    pip install datetime
```

# Execution

1. Open the terminal, call the script

Example: 

```python
   python3 get_project_details.py
```

# Output
The json output of this will print to the same directory and will include a basic timestamp of the date and hour it was printed. 


