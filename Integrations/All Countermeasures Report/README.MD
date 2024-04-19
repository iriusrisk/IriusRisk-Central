# Purpose 

The purpose of this script is to call all countermeasures from all libraries stored within your iriusrisk instance. 

# Requirements

1. Config file with the following values defined in the same directory: 

```python
  api_key = '{your_api_key}'
  sub_domain = '{your_full_domain_minus_the_api_endpoint_data}' # for example https://demo.iriusrisk.com
```

2. Install the required packages

```python

pip3 install -r requirements.txt

```
If those requirements are not being imported into your environment, you can install them manually
```python

pip3 install pandas
pip3 install requests
pip3 install tqdm
pip3 install bs4
pip3 install openpyxl
```

# Execution

Open the terminal, call the script

Example: 

```python
   python3 get_library_details_v1.py
```

# Output
The output of this will print to the same directory and will include a json file and an xlsx file. 
